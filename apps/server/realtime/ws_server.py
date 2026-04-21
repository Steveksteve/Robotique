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


clients = {}
dashboards = set()
robots = {}

EVENT_ALIASES = {
    "robot.position_updated": "robot:position",
    "mission.status_updated": "mission:updated",
    "mission.completed": "mission:completed",
}

ALLOWED_MISSION_STATUSES = {
    "CREATED",
    "ASSIGNED",
    "NAVIGATING_TO_PICKUP",
    "PICKING_UP",
    "NAVIGATING_TO_DROP",
    "COMPLETED",
    "ERROR",
}

ALLOWED_MISSION_TRANSITIONS = {
    "CREATED": {"ASSIGNED", "ERROR"},
    "ASSIGNED": {"NAVIGATING_TO_PICKUP", "ERROR"},
    "NAVIGATING_TO_PICKUP": {"PICKING_UP", "ERROR"},
    "PICKING_UP": {"NAVIGATING_TO_DROP", "ERROR"},
    "NAVIGATING_TO_DROP": {"COMPLETED", "ERROR"},
    "COMPLETED": set(),
    "ERROR": set(),
}


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def db_connect():
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        charset="utf8mb4",
        cursorclass=DictCursor,
        autocommit=True,
    )


def normalize_event_type(event_type):
    return EVENT_ALIASES.get(event_type, event_type)


def get_mission(mission_id):
    with db_connect() as connection:
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


def update_mission_status(mission_id, status):
    with db_connect() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT id FROM missions WHERE id = %s", (mission_id,))
            mission = cursor.fetchone()
            if not mission:
                return None
            cursor.execute(
                "UPDATE missions SET status = %s WHERE id = %s",
                (status, mission_id),
            )

    return get_mission(mission_id)


def insert_robot_log(mission_id, x, y):
    with db_connect() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO robot_logs (mission_id, robot_x, robot_y)
                VALUES (%s, %s, %s)
                """,
                (mission_id, x, y),
            )


def build_legacy_payload(canonical_event):
    if canonical_event["type"] == "robot:position":
        return {
            **canonical_event,
            "type": "robot.position_updated",
        }

    if canonical_event["type"] == "mission:updated":
        return {
            **canonical_event,
            "type": "mission.status_updated",
        }

    if canonical_event["type"] == "mission:completed":
        return {
            **canonical_event,
            "type": "mission.completed",
        }

    return canonical_event


def is_valid_mission_status(status):
    return status in ALLOWED_MISSION_STATUSES


def is_valid_mission_transition(current_status, next_status):
    allowed_next_statuses = ALLOWED_MISSION_TRANSITIONS.get(current_status, set())
    return next_status in allowed_next_statuses


async def safe_send(websocket, payload):
    try:
        await websocket.send(json.dumps(payload, default=str))
    except ConnectionClosed:
        pass


async def broadcast_dashboards(payload, include_legacy_alias=True):
    if not dashboards:
        return

    outgoing_payloads = [payload]
    if include_legacy_alias:
        legacy_payload = build_legacy_payload(payload)
        if legacy_payload is not payload:
            outgoing_payloads.append(legacy_payload)

    await asyncio.gather(
        *(
            safe_send(client, outgoing)
            for client in list(dashboards)
            for outgoing in outgoing_payloads
        )
    )


async def send_error(websocket, message):
    await safe_send(
        websocket,
        {"type": "server.error", "message": message, "timestamp": utc_now()},
    )


async def handle_identify(websocket, payload):
    client_type = payload.get("client_type")
    robot_id = payload.get("robot_id")

    if client_type not in {"robot", "dashboard"}:
        await send_error(websocket, "client_type must be robot or dashboard")
        return False

    if client_type == "dashboard":
        clients[websocket] = {"client_type": "dashboard", "robot_id": None}
        dashboards.add(websocket)
    else:
        if not robot_id:
            await send_error(websocket, "robot_id is required for robot clients")
            return False
        clients[websocket] = {"client_type": "robot", "robot_id": robot_id}
        robots[websocket] = robot_id
        await broadcast_dashboards(
            {
                "type": "robot.connected",
                "robot_id": robot_id,
                "timestamp": utc_now(),
            },
            include_legacy_alias=False,
        )

    await safe_send(
        websocket,
        {
            "type": "server.ack",
            "message": "identified",
            "client_type": client_type,
            "timestamp": utc_now(),
        },
    )
    return True


async def handle_position_event(websocket, payload):
    mission_id = payload.get("mission_id")
    x = payload.get("x")
    y = payload.get("y")

    if mission_id is None or x is None or y is None:
        await send_error(websocket, "mission_id, x and y are required for robot:position")
        return

    insert_robot_log(mission_id, x, y)
    event = {
        "type": "robot:position",
        "robot_id": payload.get("robot_id"),
        "mission_id": mission_id,
        "x": x,
        "y": y,
        "timestamp": payload.get("timestamp") or utc_now(),
    }
    await broadcast_dashboards(event)


async def handle_mission_updated_event(websocket, payload):
    mission_id = payload.get("mission_id")
    status = payload.get("status")

    if mission_id is None or not status:
        await send_error(websocket, "mission_id and status are required for mission:updated")
        return

    if not is_valid_mission_status(status):
        await send_error(websocket, f"invalid mission status: {status}")
        return

    current_mission = get_mission(mission_id)
    if not current_mission:
        await send_error(websocket, f"mission {mission_id} not found")
        return

    current_status = current_mission["status"]
    if not is_valid_mission_transition(current_status, status):
        await send_error(
            websocket,
            f"invalid mission transition: {current_status} -> {status}",
        )
        return

    mission = update_mission_status(mission_id, status)
    if not mission:
        await send_error(websocket, f"mission {mission_id} not found")
        return

    updated_event = {
        "type": "mission:updated",
        "robot_id": payload.get("robot_id"),
        "mission_id": mission_id,
        "status": mission["status"],
        "mission": mission,
        "timestamp": payload.get("timestamp") or utc_now(),
    }
    await broadcast_dashboards(updated_event)

    if mission["status"] == "COMPLETED":
        completed_event = {
            "type": "mission:completed",
            "robot_id": payload.get("robot_id"),
            "mission_id": mission_id,
            "status": mission["status"],
            "mission": mission,
            "timestamp": payload.get("timestamp") or utc_now(),
        }
        await broadcast_dashboards(completed_event)


async def handle_mission_completed_event(websocket, payload):
    mission_id = payload.get("mission_id")

    if mission_id is None:
        await send_error(websocket, "mission_id is required for mission:completed")
        return

    current_mission = get_mission(mission_id)
    if not current_mission:
        await send_error(websocket, f"mission {mission_id} not found")
        return

    current_status = current_mission["status"]
    target_status = "COMPLETED"

    if not is_valid_mission_transition(current_status, target_status):
        await send_error(
            websocket,
            f"invalid mission transition: {current_status} -> {target_status}",
        )
        return

    mission = update_mission_status(mission_id, target_status)
    if not mission:
        await send_error(websocket, f"mission {mission_id} not found")
        return

    completed_event = {
        "type": "mission:completed",
        "robot_id": payload.get("robot_id"),
        "mission_id": mission_id,
        "status": mission["status"],
        "mission": mission,
        "timestamp": payload.get("timestamp") or utc_now(),
    }
    await broadcast_dashboards(completed_event)


async def handle_robot_event(websocket, payload):
    event_type = normalize_event_type(payload.get("type"))

    if event_type == "robot.heartbeat":
        payload.setdefault("timestamp", utc_now())
        await broadcast_dashboards(payload, include_legacy_alias=False)
        return

    if event_type == "robot:position":
        await handle_position_event(websocket, payload)
        return

    if event_type == "mission:updated":
        await handle_mission_updated_event(websocket, payload)
        return

    if event_type == "mission:completed":
        await handle_mission_completed_event(websocket, payload)
        return

    await send_error(websocket, f"unsupported event type: {payload.get('type')}")


async def cleanup(websocket):
    client = clients.pop(websocket, None)
    dashboards.discard(websocket)
    robot_id = robots.pop(websocket, None)

    if client and client.get("client_type") == "robot" and robot_id:
        await broadcast_dashboards(
            {
                "type": "robot.disconnected",
                "robot_id": robot_id,
                "timestamp": utc_now(),
            },
            include_legacy_alias=False,
        )


async def handler(websocket):
    try:
        async for message in websocket:
            try:
                payload = json.loads(message)
            except json.JSONDecodeError:
                await send_error(websocket, "invalid json")
                continue

            if payload.get("type") == "identify":
                await handle_identify(websocket, payload)
                continue

            client = clients.get(websocket)
            if not client:
                await send_error(websocket, "identify must be sent before any event")
                continue

            if client["client_type"] != "robot":
                await send_error(websocket, "only robot clients can publish events")
                continue

            payload.setdefault("robot_id", client["robot_id"])
            await handle_robot_event(websocket, payload)
    finally:
        await cleanup(websocket)


async def main():
    async with websockets.serve(handler, WS_HOST, WS_PORT):
        print(f"WebSocket server listening on ws://{WS_HOST}:{WS_PORT}")
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())