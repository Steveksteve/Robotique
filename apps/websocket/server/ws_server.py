import asyncio
import json
import os
from datetime import datetime, timezone

import websockets
from websockets.exceptions import ConnectionClosed


HOST = os.getenv("WS_HOST", "0.0.0.0")
PORT = int(os.getenv("WS_PORT", "8765"))


robots = {}
dashboards = set()
clients = {}


def iso_now():
    return datetime.now(timezone.utc).isoformat()


async def safe_send(websocket, payload):
    try:
        await websocket.send(json.dumps(payload))
    except ConnectionClosed:
        pass


async def broadcast_dashboards(payload):
    if not dashboards:
        return
    await asyncio.gather(*(safe_send(client, payload) for client in list(dashboards)))


async def handle_identify(websocket, message):
    client_type = message.get("client_type")
    robot_id = message.get("robot_id")

    if client_type not in {"robot", "dashboard"}:
        await safe_send(
            websocket,
            {"type": "server.error", "message": "client_type must be robot or dashboard"},
        )
        return False

    clients[websocket] = {"client_type": client_type, "robot_id": robot_id}

    if client_type == "dashboard":
        dashboards.add(websocket)
    else:
        if not robot_id:
            await safe_send(
                websocket,
                {"type": "server.error", "message": "robot_id is required for robot clients"},
            )
            return False
        robots[websocket] = robot_id
        await broadcast_dashboards(
            {
                "type": "server.robot_connected",
                "robot_id": robot_id,
                "timestamp": iso_now(),
            }
        )

    await safe_send(
        websocket,
        {"type": "server.ack", "message": "identified", "client_type": client_type},
    )
    return True


async def cleanup(websocket):
    info = clients.pop(websocket, None)
    dashboards.discard(websocket)

    robot_id = robots.pop(websocket, None)
    if robot_id:
        await broadcast_dashboards(
            {
                "type": "server.robot_disconnected",
                "robot_id": robot_id,
                "timestamp": iso_now(),
            }
        )


async def handle_message(websocket, raw_message):
    try:
        message = json.loads(raw_message)
    except json.JSONDecodeError:
        await safe_send(websocket, {"type": "server.error", "message": "invalid json"})
        return

    message_type = message.get("type")

    if message_type == "identify":
        await handle_identify(websocket, message)
        return

    sender = clients.get(websocket)
    if not sender:
        await safe_send(
            websocket,
            {"type": "server.error", "message": "identify must be sent before any event"},
        )
        return

    if sender["client_type"] != "robot":
        await safe_send(
            websocket,
            {"type": "server.error", "message": "only robot clients can publish events"},
        )
        return

    message.setdefault("robot_id", sender.get("robot_id"))
    message.setdefault("timestamp", iso_now())
    await broadcast_dashboards(message)


async def handler(websocket):
    try:
        async for raw_message in websocket:
            await handle_message(websocket, raw_message)
    finally:
        await cleanup(websocket)


async def main():
    async with websockets.serve(handler, HOST, PORT):
        print(f"WebSocket relay listening on ws://{HOST}:{PORT}")
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
