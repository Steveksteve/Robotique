import os
import time
import requests
import pytest

API_BASE = os.getenv('API_BASE', 'http://localhost:8000')


def wait_for_api(timeout=60):
    start = time.time()
    while time.time() - start < timeout:
        try:
            r = requests.get(f"{API_BASE}/")
            if r.status_code == 200:
                return True
        except Exception:
            pass
        time.sleep(1)
    pytest.skip("API non disponible après attente")


def test_create_read_update_mission():
    wait_for_api()

    payload = {
        "origin": "Stock A - Rayonnage 3",
        "destination": "Poste Réception - Bureau 2",
        "object": "Boîte standard 30x20"
    }

    r = requests.post(f"{API_BASE}/missions", json=payload)
    assert r.status_code == 201, f"POST /missions failed: {r.status_code} {r.text}"
    data = r.json()
    assert 'mission_id' in data
    mission_id = data['mission_id']

    r = requests.get(f"{API_BASE}/missions")
    assert r.status_code == 200
    missions = r.json()
    assert any(str(m.get('id')) == str(mission_id) or int(m.get('id', -1)) == int(mission_id) for m in missions)

    r = requests.patch(f"{API_BASE}/missions/{mission_id}/status", json={"status": "ASSIGNED"})
    assert r.status_code in (200, 204), f"PATCH failed: {r.status_code} {r.text}"

    r = requests.get(f"{API_BASE}/missions")
    assert r.status_code == 200
    missions = r.json()
    found = next((m for m in missions if str(m.get('id')) == str(mission_id) or int(m.get('id', -1)) == int(mission_id)), None)
    assert found is not None, "Mission non trouvée après update"
    assert found.get('status') == 'ASSIGNED', f"Status attendu ASSIGNED, trouvé {found.get('status')}"
