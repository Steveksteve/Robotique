import json
import os
import threading
import time
from datetime import datetime, timezone

import requests

try:
    import websocket
except ImportError:
    websocket = None


API_BASE = os.getenv("API_BASE", "http://localhost:8000")
WS_URL = os.getenv("WS_URL", "ws://localhost:8765")
ROBOT_ID = os.getenv("ROBOT_ID", "robot-1")


def iso_now():
    return datetime.now(timezone.utc).isoformat()


class RobotRealtimeClient:
    def __init__(self):
        self.ws = None
        self.connected = False
        self.stop_event = threading.Event()
        self.worker = None

    def start(self):
        if websocket is None:
            print("websocket-client non installe, mode temps reel desactive")
            return

        self.worker = threading.Thread(target=self._run_forever, daemon=True)
        self.worker.start()

    def _run_forever(self):
        while not self.stop_event.is_set():
            try:
                self.ws = websocket.create_connection(WS_URL, timeout=5)
                self.connected = True
                self._send(
                    {
                        "type": "identify",
                        "client_type": "robot",
                        "robot_id": ROBOT_ID,
                    }
                )
                print(f"WebSocket connecte a {WS_URL}")

                while not self.stop_event.is_set():
                    self.publish_heartbeat()
                    time.sleep(5)
            except Exception as exc:
                self.connected = False
                print(f"Connexion WebSocket indisponible: {exc}")
                time.sleep(2)
            finally:
                if self.ws is not None:
                    try:
                        self.ws.close()
                    except Exception:
                        pass
                    self.ws = None

    def _send(self, payload):
        if not self.connected or self.ws is None:
            return
        self.ws.send(json.dumps(payload))

    def publish_heartbeat(self):
        self._send(
            {
                "type": "robot.heartbeat",
                "robot_id": ROBOT_ID,
                "timestamp": iso_now(),
            }
        )

    def publish_position(self, x, y, battery=100):
        self._send(
            {
                "type": "robot.position_updated",
                "robot_id": ROBOT_ID,
                "x": x,
                "y": y,
                "battery": battery,
                "timestamp": iso_now(),
            }
        )

    def publish_status(self, mission_id, status):
        self._send(
            {
                "type": "mission.status_updated",
                "robot_id": ROBOT_ID,
                "mission_id": mission_id,
                "status": status,
                "timestamp": iso_now(),
            }
        )

    def stop(self):
        self.stop_event.set()
        if self.ws is not None:
            try:
                self.ws.close()
            except Exception:
                pass


class RobotClient:
    def __init__(self):
        self.session = requests.Session()
        self.realtime = RobotRealtimeClient()

    def get_missions(self):
        try:
            response = self.session.get(f"{API_BASE}/missions")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as exc:
            print("Erreur recuperation missions :", exc)
            return None

    def update_status(self, mission_id, status):
        try:
            response = self.session.patch(
                f"{API_BASE}/missions/{mission_id}/status",
                json={"status": status},
            )
            response.raise_for_status()
            payload = response.json()
            self.realtime.publish_status(mission_id, status)
            return payload
        except requests.RequestException as exc:
            print("Erreur mise a jour mission :", exc)
            return None

    def run(self):
        self.realtime.start()

        try:
            while True:
                missions = self.get_missions()

                if missions:
                    for index, mission in enumerate(missions):
                        if mission["status"] == "CREATED":
                            print(f"Mission recue : {mission['id']}")
                            self.realtime.publish_position(x=index + 1, y=index + 2, battery=95)
                            self.update_status(mission["id"], "NAVIGATING_TO_PICKUP")
                            time.sleep(3)
                            self.realtime.publish_position(x=index + 2, y=index + 3, battery=91)
                            self.update_status(mission["id"], "COMPLETED")

                time.sleep(5)
        finally:
            self.realtime.stop()


if __name__ == "__main__":
    RobotClient().run()
