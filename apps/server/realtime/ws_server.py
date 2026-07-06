import asyncio
import json
import os
from datetime import datetime, timezone

import pymysql
import websockets
from pymysql.cursors import DictCursor
from websockets.exceptions import ConnectionClosed


WS_HOST = os.getenv("WS_HOST", "0.0.0.0")
WS_PORT = int(os.getenv("WS_PORT", "8765"))

DB_HOST = os.getenv("DB_HOST", "db")
DB_NAME = os.getenv("DB_NAME", "raa_db")
DB_USER = os.getenv("DB_USER", "raa")
DB_PASSWORD = os.getenv("DB_PASSWORD", "raapass")

dashboards = set()
robots = {}
clients = {}

MISSION_FLOW = [
    "CREATED",
    "ASSIGNED",
    "NAVIGATING_TO_PICKUP",
    "SCANNING_QR",
    "PICKING_UP",
    "NAVIGATING_TO_DROP",
    "DROPPING_OFF",
    "COMPLETED",
]

TERMINAL_STATUSES = {"COMPLETED", "ERROR"}
ALLOWED_STATUSES = set(MISSION_FLOW + ["ERROR"])


def now():
    return datetime.now(timezone.utc).isoformat()


def db():
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        charset="utf8mb4",
        cursorclass=DictCursor,
        autocommit=True,
    )


def to_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def get_mission(mission_id):
    mission_id = to_int(mission_id)

    if mission_id is None:
        return None

    with db() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, origin, destination, object, status, created_at, updated_at
                FROM missions
                WHERE id = %s
                """,
                (mission_id,),
            )
            return cursor.fetchone()


def get_active_missions():
    with db() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, origin, destination, object, status, created_at, updated_at
                FROM missions
                WHERE status IN (
                    'ASSIGNED',
                    'NAVIGATING_TO_PICKUP',
                    'SCANNING_QR',
                    'PICKING_UP',
                    'NAVIGATING_TO_DROP',
                    'DROPPING_OFF'
                )
                ORDER BY id ASC
                """
            )
            return cursor.fetchall()


def set_mission_status(mission_id, status):
    mission_id = to_int(mission_id)

    if mission_id is None:
        return None

    with db() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE missions SET status = %s WHERE id = %s",
                (status, mission_id),
            )

    return get_mission(mission_id)


def transition_mission(mission_id, target_status):
    mission = get_mission(mission_id)

    if not mission:
        return None, "mission not found"

    current_status = mission["status"]

    if target_status == current_status:
        return mission, None

    if current_status in TERMINAL_STATUSES:
        return None, f"mission already terminal: {current_status}"

    if target_status == "ERROR":
        return set_mission_status(mission_id, "ERROR"), None

    if target_status not in MISSION_FLOW or current_status not in MISSION_FLOW:
        return None, f"invalid transition: {current_status} -> {target_status}"

    current_index = MISSION_FLOW.index(current_status)
    target_index = MISSION_FLOW.index(target_status)

    if target_index <= current_index:
        return None, f"invalid transition: {current_status} -> {target_status}"

    mission_after_update = mission

    for status in MISSION_FLOW[current_index + 1 : target_index + 1]:
        mission_after_update = set_mission_status(mission_id, status)

    return mission_after_update, None


def insert_robot_log(mission_id, x, y):
    mission_id = to_int(mission_id)

    if mission_id is None:
        return

    with db() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO robot_logs (mission_id, robot_x, robot_y)
                VALUES (%s, %s, %s)
                """,
                (mission_id, x, y),
            )


async def safe_send(websocket, payload):
    try:
        await websocket.send(json.dumps(payload, default=str))
        return True
    except ConnectionClosed:
        return False


async def send_error(websocket, message):
    await safe_send(
        websocket,
        {
            "type": "server.error",
            "message": message,
            "timestamp": now(),
        },
    )


async def broadcast_to_dashboards(payload):
    if not dashboards:
        return

    await asyncio.gather(
        *(safe_send(ws, payload) for ws in list(dashboards)),
        return_exceptions=True,
    )


async def send_to_robots(payload, robot_id=None):
    sent_count = 0

    for websocket, robot_data in list(robots.items()):
        if robot_id and robot_data.get("robot_id") != robot_id:
            continue

        ok = await safe_send(websocket, payload)

        if ok:
            sent_count += 1

    return sent_count


async def publish_mission_update(mission, robot_id=None, event_type="mission:updated"):
    payload = {
        "type": event_type,
        "robot_id": robot_id,
        "mission_id": mission["id"],
        "status": mission["status"],
        "mission": mission,
        "timestamp": now(),
    }

    await broadcast_to_dashboards(payload)

    if mission["status"] == "COMPLETED":
        await broadcast_to_dashboards(
            {
                **payload,
                "type": "mission:completed",
            }
        )


async def identify_client(websocket, payload):
    client_type = payload.get("client_type")
    robot_id = payload.get("robot_id")

    if client_type == "dashboard":
        clients[websocket] = {
            "client_type": "dashboard",
            "robot_id": None,
        }

        dashboards.add(websocket)

    elif client_type == "robot":
        if not robot_id:
            await send_error(websocket, "robot_id required")
            return

        clients[websocket] = {
            "client_type": "robot",
            "robot_id": robot_id,
        }

        robots[websocket] = {
            "robot_id": robot_id,
            "last_seen": now(),
            "active_mission_id": payload.get("mission_id"),
        }

        await broadcast_to_dashboards(
            {
                "type": "robot.connected",
                "robot_id": robot_id,
                "timestamp": now(),
            }
        )

        active_missions = get_active_missions()

        for mission in active_missions:
            await safe_send(
                websocket,
                {
                    "type": "mission:assigned",
                    "robot_id": robot_id,
                    "mission_id": mission["id"],
                    "mission": mission,
                    "timestamp": now(),
                },
            )

    else:
        await send_error(websocket, "client_type must be dashboard or robot")
        return

    await safe_send(
        websocket,
        {
            "type": "server.ack",
            "message": "identified",
            "client_type": client_type,
            "timestamp": now(),
        },
    )


async def handle_dashboard_event(websocket, payload):
    event_type = payload.get("type")

    if event_type == "mission:assign":
        mission_id = to_int(payload.get("mission_id"))
        robot_id = payload.get("robot_id")

        if mission_id is None:
            await send_error(websocket, "mission_id required")
            return

        mission, error = transition_mission(mission_id, "ASSIGNED")

        if error:
            await send_error(websocket, error)
            return

        await publish_mission_update(
            mission,
            robot_id=robot_id,
            event_type="mission:assigned",
        )

        robot_payload = {
            "type": "mission:assigned",
            "robot_id": robot_id,
            "mission_id": mission_id,
            "mission": mission,
            "timestamp": now(),
        }

        sent_count = await send_to_robots(robot_payload, robot_id)

        await broadcast_to_dashboards(
            {
                "type": "mission:assigned",
                "robot_id": robot_id,
                "mission_id": mission_id,
                "mission": mission,
                "message": f"Mission #{mission_id} envoyée à {sent_count} robot(s)",
                "timestamp": now(),
            }
        )

        return

    if event_type == "robot:emergency_stop":
        await handle_emergency_stop(websocket, payload)
        return

    await send_error(websocket, f"unsupported dashboard event: {event_type}")


async def handle_robot_event(websocket, payload):
    event_type = payload.get("type")
    client = clients.get(websocket, {})
    robot_id = client.get("robot_id")

    payload.setdefault("robot_id", robot_id)

    if websocket in robots:
        robots[websocket]["last_seen"] = now()

    if event_type == "robot.heartbeat":
        if websocket in robots:
            robots[websocket]["active_mission_id"] = (
                payload.get("mission_id") or robots[websocket].get("active_mission_id")
            )

        await broadcast_to_dashboards(
            {
                "type": "robot.heartbeat",
                "robot_id": robot_id,
                "mission_id": payload.get("mission_id"),
                "timestamp": now(),
            }
        )

        return

    if event_type == "robot:position":
        mission_id = to_int(payload.get("mission_id"))
        x = payload.get("x")
        y = payload.get("y")

        if x is None or y is None:
            await send_error(websocket, "x and y required")
            return

        if mission_id is not None:
            insert_robot_log(mission_id, x, y)

        await broadcast_to_dashboards(
            {
                "type": "robot:position",
                "robot_id": robot_id,
                "mission_id": mission_id,
                "x": x,
                "y": y,
                "timestamp": now(),
            }
        )

        return

    if event_type in ["mission:updated", "mission.status_updated", "mission:completed", "mission.completed"]:
        mission_id = to_int(payload.get("mission_id"))

        if event_type in ["mission:completed", "mission.completed"]:
            target_status = "COMPLETED"
        else:
            target_status = payload.get("status")

        if mission_id is None or not target_status:
            await send_error(websocket, "mission_id and status required")
            return

        if target_status not in ALLOWED_STATUSES:
            await send_error(websocket, f"invalid status: {target_status}")
            return

        mission, error = transition_mission(mission_id, target_status)

        if error:
            await send_error(websocket, error)
            return

        if websocket in robots:
            robots[websocket]["active_mission_id"] = mission_id

            if mission["status"] in TERMINAL_STATUSES:
                robots[websocket]["active_mission_id"] = None

        await publish_mission_update(mission, robot_id=robot_id)
        return

    if event_type == "robot:emergency_stop":
        await handle_emergency_stop(websocket, payload)
        return

    await send_error(websocket, f"unsupported robot event: {event_type}")


async def handle_emergency_stop(websocket, payload):
    client = clients.get(websocket, {})
    robot_id = payload.get("robot_id") or client.get("robot_id")
    mission_id = to_int(payload.get("mission_id"))
    reason = payload.get("reason") or "Emergency stop requested"

    if mission_id is None and websocket in robots:
        mission_id = to_int(robots[websocket].get("active_mission_id"))

    mission = None

    if mission_id is not None:
        current_mission = get_mission(mission_id)

        if current_mission and current_mission["status"] not in TERMINAL_STATUSES:
            mission, _ = transition_mission(mission_id, "ERROR")

    event = {
        "type": "robot:emergency_stop",
        "robot_id": robot_id,
        "mission_id": mission_id,
        "mission": mission,
        "reason": reason,
        "timestamp": now(),
    }

    if client.get("client_type") == "dashboard":
        await send_to_robots(event, robot_id)

    await broadcast_to_dashboards(event)

    if mission:
        await publish_mission_update(mission, robot_id=robot_id)


async def cleanup(websocket):
    dashboards.discard(websocket)

    client = clients.pop(websocket, None)
    robot = robots.pop(websocket, None)

    if client and client.get("client_type") == "robot" and robot:
        await broadcast_to_dashboards(
            {
                "type": "robot.disconnected",
                "robot_id": robot.get("robot_id"),
                "timestamp": now(),
            }
        )


async def handler(websocket):
    try:
        async for raw_message in websocket:
            try:
                payload = json.loads(raw_message)
            except json.JSONDecodeError:
                await send_error(websocket, "invalid json")
                continue

            if payload.get("type") == "identify":
                await identify_client(websocket, payload)
                continue

            client = clients.get(websocket)

            if not client:
                await send_error(websocket, "identify required before events")
                continue

            if client["client_type"] == "dashboard":
                await handle_dashboard_event(websocket, payload)
            elif client["client_type"] == "robot":
                await handle_robot_event(websocket, payload)
            else:
                await send_error(websocket, "unknown client type")

    finally:
        await cleanup(websocket)


async def main():
    async with websockets.serve(handler, WS_HOST, WS_PORT):
        print(f"WebSocket server listening on ws://{WS_HOST}:{WS_PORT}")
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
