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


def utc_now():
    return datetime.now(timezone.utc).isoformat()


class RobotSocketClient:
    def __init__(self):
        self.connection = None
        self.connected = False
        self.stop_event = threading.Event()
        self.thread = None

    def start(self):
        if websocket is None:
            print("websocket-client non installe, WebSocket desactive")
            return

        self.thread = threading.Thread(target=self._connect_loop, daemon=True)
        self.thread.start()

    def _connect_loop(self):
        while not self.stop_event.is_set():
            try:
                self.connection = websocket.create_connection(WS_URL, timeout=5)
                self.connected = True
                self.send(
                    {
                        "type": "identify",
                        "client_type": "robot",
                        "robot_id": ROBOT_ID,
                    }
                )
                print(f"Robot connecte au WebSocket {WS_URL}")

                while not self.stop_event.is_set():
                    self.send(
                        {
                            "type": "robot.heartbeat",
                            "robot_id": ROBOT_ID,
                            "timestamp": utc_now(),
                        }
                    )
                    time.sleep(5)
            except Exception as exc:
                self.connected = False
                print(f"WebSocket indisponible: {exc}")
                time.sleep(2)
            finally:
                if self.connection is not None:
                    try:
                        self.connection.close()
                    except Exception:
                        pass
                    self.connection = None

    def send(self, payload):
        if not self.connected or self.connection is None:
            return
        self.connection.send(json.dumps(payload))

    def stop(self):
        self.stop_event.set()
        if self.connection is not None:
            try:
                self.connection.close()
            except Exception:
                pass


class RobotClient:
    def __init__(self):
        self.session = requests.Session()
        self.socket_client = RobotSocketClient()

    def get_missions(self):
        try:
            response = self.session.get(f"{API_BASE}/missions")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as exc:
            print("Erreur recuperation missions :", exc)
            return None

    def publish_position(self, mission_id, x, y):
        self.socket_client.send(
            {
                "type": "robot:position",
                "robot_id": ROBOT_ID,
                "mission_id": mission_id,
                "x": x,
                "y": y,
                "timestamp": utc_now(),
            }
        )

    def publish_status(self, mission_id, status):
        self.socket_client.send(
            {
                "type": "mission:updated",
                "robot_id": ROBOT_ID,
                "mission_id": mission_id,
                "status": status,
                "timestamp": utc_now(),
            }
        )

    def run(self):
        self.socket_client.start()
        try:
            while True:
                missions = self.get_missions()
                if missions:
                    for index, mission in enumerate(missions):
                        if mission["status"] == "CREATED":
                            mission_id = mission["id"]
                            print(f"Mission recue : {mission_id}")
                            self.publish_status(mission_id, "ASSIGNED")
                            time.sleep(1)
                            self.publish_position(mission_id, index + 1, index + 2)
                            self.publish_status(mission_id, "NAVIGATING_TO_PICKUP")
                            time.sleep(3)
                            self.publish_position(mission_id, index + 2, index + 3)
                            self.publish_status(mission_id, "COMPLETED")
                time.sleep(5)
        except KeyboardInterrupt:
            print("Arret du client robot")
        finally:
            self.socket_client.stop()


if __name__ == "__main__":
    RobotClient().run()