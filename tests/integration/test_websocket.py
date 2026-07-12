import json
import os
import time

import pytest
import requests
import websocket

API_BASE = os.getenv("API_BASE", "http://localhost:8000")
WS_URL = os.getenv("WS_URL", "ws://localhost:8765")
WEB_BASE = os.getenv("WEB_BASE", "http://localhost:8080")

FULL_ROBOT_FLOW = [
    "NAVIGATING_TO_PICKUP",
    "SCANNING_QR",
    "PICKING_UP",
    "NAVIGATING_TO_DROP",
    "DROPPING_OFF",
    "COMPLETED",
]


def wait_for_service(url, timeout=60):
    start = time.time()
    while time.time() - start < timeout:
        try:
            response = requests.get(url, timeout=2)
            if response.status_code < 500:
                return True
        except Exception:
            pass
        time.sleep(1)
    pytest.skip(f"Service indisponible: {url}")


def send(ws, payload):
    ws.send(json.dumps(payload))


def recv_until(ws, predicate, timeout=10):
    deadline = time.time() + timeout
    last_event = None
    while time.time() < deadline:
        ws.settimeout(max(0.1, deadline - time.time()))
        try:
            event = json.loads(ws.recv())
        except websocket.WebSocketTimeoutException:
            continue
        last_event = event
        if predicate(event):
            return event
    raise AssertionError(f"Timed out waiting for event. Last event: {last_event}")


def create_mission():
    response = requests.post(
        f"{API_BASE}/missions",
        json={
            "origin": "Point A",
            "destination": "Point B",
            "object": "Colis WS",
            "expected_qr": "a",
        },
        timeout=5,
    )
    assert response.status_code == 201, response.text
    return int(response.json()["mission_id"])


def poll_mission_status(mission_id, expected_status, timeout=10):
    deadline = time.time() + timeout
    last = None
    while time.time() < deadline:
        response = requests.get(f"{API_BASE}/missions/{mission_id}", timeout=5)
        assert response.status_code == 200
        last = response.json()
        if last["status"] == expected_status:
            return last
        time.sleep(0.5)
    raise AssertionError(f"Expected {expected_status}, got {last}")


def test_web_front_is_served():
    wait_for_service(f"{WEB_BASE}/")
    response = requests.get(f"{WEB_BASE}/", timeout=5)
    assert response.status_code == 200
    assert "<div id=\"root\"></div>" in response.text


def test_websocket_dashboard_to_robot_mission_flow():
    wait_for_service(f"{API_BASE}/health")
    mission_id = create_mission()

    robot = websocket.create_connection(WS_URL, timeout=5)
    dashboard = websocket.create_connection(WS_URL, timeout=5)

    try:
        send(robot, {"type": "identify", "client_type": "robot", "robot_id": "pytest-robot"})
        recv_until(robot, lambda event: event.get("type") == "server.ack")

        send(dashboard, {"type": "identify", "client_type": "dashboard"})
        recv_until(dashboard, lambda event: event.get("type") == "server.ack")

        send(dashboard, {"type": "mission:assign", "mission_id": mission_id, "robot_id": "pytest-robot"})
        assigned = recv_until(robot, lambda event: event.get("type") == "mission:assigned")
        assert int(assigned["mission_id"]) == mission_id
        assert assigned["mission"]["status"] == "ASSIGNED"

        for index, status in enumerate(FULL_ROBOT_FLOW):
            send(
                robot,
                {
                    "type": "mission:updated" if status != "COMPLETED" else "mission:completed",
                    "robot_id": "pytest-robot",
                    "mission_id": mission_id,
                    "status": status,
                    "x": 120 + index,
                    "y": 150 + index,
                },
            )
            poll_mission_status(mission_id, status)

        completed = recv_until(
            dashboard,
            lambda event: event.get("type") in {"mission:completed", "mission:updated"}
            and int(event.get("mission_id", -1)) == mission_id
            and event.get("mission", {}).get("status") == "COMPLETED",
        )
        assert completed["mission"]["status"] == "COMPLETED"

    finally:
        robot.close()
        dashboard.close()
