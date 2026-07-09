from __future__ import annotations

import types

import pytest

from m3pro_teacher_vision.mission_executor_node import (
    MapPoint,
    MissionExecutorNode,
    RobotRealtimeBridge,
    yaw_to_quaternion,
)


class FakeLogger:
    def info(self, *args, **kwargs):
        return None

    def warning(self, *args, **kwargs):
        return None

    def error(self, *args, **kwargs):
        return None

    def debug(self, *args, **kwargs):
        return None


def test_yaw_to_quaternion_returns_expected_values():
    qx, qy, qz, qw = yaw_to_quaternion(0.0)

    assert qx == 0.0
    assert qy == 0.0
    assert qz == 0.0
    assert qw == 1.0


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (True, True),
        (False, False),
        (1, True),
        (0, False),
        ("yes", True),
        ("off", False),
        ("  On  ", True),
        ("no", False),
    ],
)
def test_as_bool_handles_common_values(value, expected):
    assert MissionExecutorNode.as_bool(value) is expected


def test_point_from_mission_uses_defaults_when_values_are_missing():
    node = MissionExecutorNode.__new__(MissionExecutorNode)
    default = MapPoint(1.0, 2.0, 3.0)

    point = MissionExecutorNode.point_from_mission(node, {}, "pickup", default)

    assert point == default


def test_read_qr_dry_run_returns_simulated_qr():
    node = MissionExecutorNode.__new__(MissionExecutorNode)
    node.dry_run = True
    node.simulated_qr = "b"
    node.get_logger = lambda: FakeLogger()

    assert MissionExecutorNode.read_qr(node) == "b"


def test_realtime_bridge_publishes_status_and_position_payloads():
    payloads = []
    bridge = RobotRealtimeBridge("ws://example", "robot-1", FakeLogger())
    bridge.send = lambda payload: payloads.append(payload) or True

    bridge.publish_status(7, "NAVIGATING_TO_PICKUP", "arrived")
    bridge.publish_position(7, 12.5, 8.75)

    assert payloads[0]["type"] == "mission:updated"
    assert payloads[0]["mission_id"] == 7
    assert payloads[0]["status"] == "NAVIGATING_TO_PICKUP"
    assert payloads[0]["error_reason"] == "arrived"
    assert payloads[1]["type"] == "robot:position"
    assert payloads[1]["x"] == 12.5
    assert payloads[1]["y"] == 8.75


def test_execute_mission_success_flow_updates_each_step():
    calls = []

    def set_status(mission_id, status, error_reason=None):
        calls.append(("set_status", status, error_reason))
        return {"mission_id": mission_id, "status": status}

    runner = types.SimpleNamespace(
        dry_run=True,
        robot_id="pytest-robot",
        default_pickup=MapPoint(2.62, 6.12, -1.9),
        default_dropoff=MapPoint(1.32, 2.18, -1.9),
        point_from_mission=lambda mission, prefix, default: default,
        set_status=set_status,
        navigate_to=lambda point: calls.append(("navigate_to", point)) or True,
        read_qr=lambda: "a",
        pick_object=lambda: calls.append(("pick_object", None)) or True,
        drop_object=lambda: calls.append(("drop_object", None)) or True,
        publish_position=lambda mission_id, point: calls.append(("publish_position", mission_id, point)),
    )

    MissionExecutorNode.execute_mission(
        runner,
        {"id": 42, "status": "CREATED", "expected_qr": "a"},
    )

    assert [entry[1] for entry in calls if entry[0] == "set_status"] == [
        "ASSIGNED",
        "NAVIGATING_TO_PICKUP",
        "SCANNING_QR",
        "PICKING_UP",
        "NAVIGATING_TO_DROP",
        "DROPPING_OFF",
        "COMPLETED",
    ]
    assert ("publish_position", 42, runner.default_pickup) in calls
    assert ("publish_position", 42, runner.default_dropoff) in calls
    assert ("pick_object", None) in calls
    assert ("drop_object", None) in calls


def test_execute_mission_stops_on_qr_mismatch():
    calls = []

    def set_status(mission_id, status, error_reason=None):
        calls.append((status, error_reason))
        return {"mission_id": mission_id, "status": status}

    runner = types.SimpleNamespace(
        dry_run=True,
        robot_id="pytest-robot",
        default_pickup=MapPoint(2.62, 6.12, -1.9),
        default_dropoff=MapPoint(1.32, 2.18, -1.9),
        point_from_mission=lambda mission, prefix, default: default,
        set_status=set_status,
        navigate_to=lambda point: True,
        read_qr=lambda: "wrong",
        pick_object=lambda: (_ for _ in ()).throw(AssertionError("pick_object should not run")),
        drop_object=lambda: (_ for _ in ()).throw(AssertionError("drop_object should not run")),
        publish_position=lambda mission_id, point: None,
    )

    MissionExecutorNode.execute_mission(
        runner,
        {"id": 7, "status": "CREATED", "expected_qr": "expected"},
    )

    assert calls[-1][0] == "ERROR"
    assert "QR incorrect" in calls[-1][1]
