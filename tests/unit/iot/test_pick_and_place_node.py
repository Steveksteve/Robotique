from __future__ import annotations

from m3pro_teacher_vision.pick_and_place_node import PickAndPlaceNode, clamp, rad_to_servo


def test_clamp_limits_values():
    assert clamp(5, 0, 3) == 3
    assert clamp(-1, 0, 3) == 0
    assert clamp(2, 0, 3) == 2


def test_rad_to_servo_centers_at_90_degrees():
    assert rad_to_servo(0.0) == 90.0


def test_compute_ik_returns_angles_for_reachable_target():
    node = PickAndPlaceNode.__new__(PickAndPlaceNode)
    node.arm_base_x = 0.02
    node.arm_base_z = 0.24
    node.L1 = 0.11
    node.L2 = 0.11
    node.L3 = 0.12

    joints = node.compute_ik(0.15, 0.0, 0.02)

    assert joints is not None
    assert len(joints) == 5


def test_compute_ik_returns_none_for_unreachable_target():
    node = PickAndPlaceNode.__new__(PickAndPlaceNode)
    node.arm_base_x = 0.02
    node.arm_base_z = 0.24
    node.L1 = 0.11
    node.L2 = 0.11
    node.L3 = 0.12

    assert node.compute_ik(1.0, 0.0, 0.24) is None
