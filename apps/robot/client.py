import requests
import time

API_BASE = "http://localhost:8000"

class RobotClient:

    def __init__(self):
        self.session = requests.Session()

    def get_missions(self):
        try:
            response = self.session.get(f"{API_BASE}/missions")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print("Erreur récupération missions :", e)
            return None

    def update_status(self, mission_id, status):
        try:
            response = self.session.patch(
                f"{API_BASE}/missions/{mission_id}",
                json={"status": status}
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print("Erreur mise à jour mission :", e)
            return None


if __name__ == "__main__":
    client = RobotClient()

    while True:
        missions = client.get_missions()

        if missions:
            for mission in missions:
                if mission["status"] == "CREATED":
                    print(f"Mission reçue : {mission['id']}")

                    client.update_status(mission["id"], "NAVIGATING")

                    time.sleep(3)

                    client.update_status(mission["id"], "COMPLETED")

        time.sleep(5)