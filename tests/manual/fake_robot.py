import asyncio
import json
import random
import websockets

WS_URL = "ws://localhost:8765"
ROBOT_ID = "raa-fake-robot-01"


async def send(ws, payload):
    await ws.send(json.dumps(payload))


async def heartbeat(ws, get_mission_id):
    while True:
        await send(ws, {
            "type": "robot.heartbeat",
            "robot_id": ROBOT_ID,
            "mission_id": get_mission_id()
        })
        await asyncio.sleep(2)


async def send_position(ws, mission_id, count=5):
    for _ in range(count):
        await send(ws, {
            "type": "robot:position",
            "robot_id": ROBOT_ID,
            "mission_id": mission_id,
            "x": 160 + random.randint(-70, 70),
            "y": 160 + random.randint(-70, 70)
        })
        await asyncio.sleep(1)


async def update_status(ws, mission_id, status):
    print(f"Mission #{mission_id} -> {status}")

    await send(ws, {
        "type": "mission:updated",
        "robot_id": ROBOT_ID,
        "mission_id": mission_id,
        "status": status
    })


async def main():
    current_mission_id = None

    def get_current_mission_id():
        return current_mission_id

    async with websockets.connect(WS_URL) as ws:
        await send(ws, {
            "type": "identify",
            "client_type": "robot",
            "robot_id": ROBOT_ID
        })

        print("Fake robot connected to WebSocket.")

        asyncio.create_task(heartbeat(ws, get_current_mission_id))

        async for message in ws:
            event = json.loads(message)
            print("Received:", event)

            if event.get("type") == "mission:assigned":
                current_mission_id = event.get("mission_id")

                await asyncio.sleep(1)

                await update_status(ws, current_mission_id, "NAVIGATING_TO_PICKUP")
                await send_position(ws, current_mission_id, 5)

                await update_status(ws, current_mission_id, "SCANNING_QR")
                await asyncio.sleep(1)

                await update_status(ws, current_mission_id, "PICKING_UP")
                await asyncio.sleep(2)

                await update_status(ws, current_mission_id, "NAVIGATING_TO_DROP")
                await send_position(ws, current_mission_id, 5)

                await update_status(ws, current_mission_id, "DROPPING_OFF")
                await asyncio.sleep(1)

                await update_status(ws, current_mission_id, "COMPLETED")

                current_mission_id = None


if __name__ == "__main__":
    asyncio.run(main())