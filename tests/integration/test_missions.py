import os
import time

import pytest
import requests

API_BASE = os.getenv("API_BASE", "http://localhost:8000")

MISSION_STATUSES = [
    "ASSIGNED",
    "NAVIGATING_TO_PICKUP",
    "SCANNING_QR",
    "PICKING_UP",
    "NAVIGATING_TO_DROP",
    "DROPPING_OFF",
    "COMPLETED",
]


def wait_for_api(timeout=60):
    start = time.time()
    while time.time() - start < timeout:
        try:
            response = requests.get(f"{API_BASE}/health", timeout=2)
            if response.status_code == 200:
                return True
        except Exception:
            pass
        time.sleep(1)
    pytest.skip("API non disponible après attente")


def create_mission(**overrides):
    payload = {
        "origin": "Stock A - Rayonnage 3",
        "destination": "Poste Réception - Bureau 2",
        "object": "Boîte standard 30x20",
        "expected_qr": "a",
        "pickup_x": 2.62,
        "pickup_y": 6.12,
        "pickup_theta": -1.90,
        "dropoff_x": 1.32,
        "dropoff_y": 2.18,
        "dropoff_theta": -1.90,
    }
    payload.update(overrides)

    response = requests.post(f"{API_BASE}/missions", json=payload, timeout=5)
    assert response.status_code == 201, response.text
    data = response.json()
    assert "mission_id" in data
    return int(data["mission_id"]), data["mission"]


def get_mission(mission_id):
    response = requests.get(f"{API_BASE}/missions/{mission_id}", timeout=5)
    assert response.status_code == 200, response.text
    return response.json()


def patch_status(mission_id, status, expected_status=200):
    response = requests.patch(
        f"{API_BASE}/missions/{mission_id}/status",
        json={"status": status, "robot_id": "pytest-robot"},
        timeout=5,
    )
    assert response.status_code == expected_status, response.text
    return response.json() if response.text else None


def test_create_read_full_status_workflow_and_logs():
    wait_for_api()

    mission_id, mission = create_mission()
    assert mission["status"] == "CREATED"
    assert mission["expected_qr"] == "a"

    listed = requests.get(f"{API_BASE}/missions", timeout=5)
    assert listed.status_code == 200
    assert any(int(item["id"]) == mission_id for item in listed.json())

    for status in MISSION_STATUSES:
        body = patch_status(mission_id, status)
        assert body["mission"]["status"] == status

    assert get_mission(mission_id)["status"] == "COMPLETED"

    logs = requests.get(f"{API_BASE}/logs", timeout=5)
    assert logs.status_code == 200
    assert any(int(item["mission_id"]) == mission_id for item in logs.json())


def test_invalid_transition_is_rejected():
    wait_for_api()
    mission_id, _ = create_mission(object="Transition guard")

    response = requests.patch(
        f"{API_BASE}/missions/{mission_id}/status",
        json={"status": "COMPLETED"},
        timeout=5,
    )
    assert response.status_code == 409
    assert response.json()["error"] == "Invalid transition"


def test_map_points_are_seeded():
    wait_for_api()
    response = requests.get(f"{API_BASE}/map-points", timeout=5)
    assert response.status_code == 200
    names = {item["name"] for item in response.json()}
    assert {"pickup_default", "dropoff_default"}.issubset(names)
