import asyncio
import json
import os
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Tuple

import pymysql
import websockets
from pymysql.cursors import DictCursor
from websockets.exceptions import ConnectionClosed


WS_HOST = os.getenv("WS_HOST", "0.0.0.0")
WS_PORT = int(os.getenv("WS_PORT", "8765"))
HEARTBEAT_TIMEOUT_SECONDS = int(os.getenv("HEARTBEAT_TIMEOUT_SECONDS", "20"))
HEARTBEAT_WATCH_INTERVAL_SECONDS = int(os.getenv("HEARTBEAT_WATCH_INTERVAL_SECONDS", "5"))

DB_HOST = os.getenv("DB_HOST", "db")
DB_NAME = os.getenv("DB_NAME", "raa_db")
DB_USER = os.getenv("DB_USER", "raa")
DB_PASSWORD = os.getenv("DB_PASSWORD", "raapass")

# Connected clients. Keys are websocket objects.
dashboards = set()
robots: Dict[Any, Dict[str, Any]] = {}
clients: Dict[Any, Dict[str, Any]] = {}

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
ACTIVE_STATUSES = tuple(status for status in MISSION_FLOW if status not in {"CREATED", "COMPLETED"})


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def now_ts() -> float:
    return datetime.now(timezone.utc).timestamp()


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


def to_int(value) -> Optional[int]:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def to_float(value) -> Optional[float]:
    try:
        if value is None:
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def get_mission(mission_id) -> Optional[Dict[str, Any]]:
    mission_id = to_int(mission_id)
    if mission_id is None:
        return None

    with db() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT *
                FROM missions
                WHERE id = %s
                """,
                (mission_id,),
            )
            return cursor.fetchone()


def get_active_missions():
    with db() as connection:
        with connection.cursor() as cursor:
            placeholders = ",".join(["%s"] * len(ACTIVE_STATUSES))
            cursor.execute(
                f"""
                SELECT *
                FROM missions
                WHERE status IN ({placeholders})
                ORDER BY id ASC
                """,
                ACTIVE_STATUSES,
            )
            return cursor.fetchall()


def set_mission_status(mission_id, status: str, error_reason: Optional[str] = None):
    mission_id = to_int(mission_id)
    if mission_id is None:
        return None

    with db() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE missions
                SET status = %s, error_reason = %s
                WHERE id = %s
                """,
                (status, error_reason if status == "ERROR" else None, mission_id),
            )

    return get_mission(mission_id)


def transition_mission(mission_id, target_status: str, error_reason: Optional[str] = None) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    mission = get_mission(mission_id)

    if not mission:
        return None, "mission not found"

    current_status = mission["status"]

    if target_status == current_status:
        return mission, None

    if current_status in TERMINAL_STATUSES:
        return None, f"mission already terminal: {current_status}"

    if target_status == "ERROR":
        return set_mission_status(mission_id, "ERROR", error_reason or "Mission stopped"), None

    if target_status not in MISSION_FLOW or current_status not in MISSION_FLOW:
        return None, f"invalid transition: {current_status} -> {target_status}"

    current_index = MISSION_FLOW.index(current_status)
    target_index = MISSION_FLOW.index(target_status)

    if target_index != current_index + 1:
        return None, f"invalid transition: {current_status} -> {target_status}"

    return set_mission_status(mission_id, target_status), None


def insert_robot_log(
    mission_id=None,
    x=None,
    y=None,
    robot_id: Optional[str] = None,
    status: Optional[str] = None,
    message: Optional[str] = None,
):
    mission_id = to_int(mission_id)
    x = to_float(x)
    y = to_float(y)

    with db() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO robot_logs (mission_id, robot_id, robot_x, robot_y, status, message)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (mission_id, robot_id, x, y, status, message),
            )


async def safe_send(websocket, payload):
    try:
        await websocket.send(json.dumps(payload, default=str))
        return True
    except ConnectionClosed:
        await cleanup(websocket)
        return False
    except Exception:
        await cleanup(websocket)
        return False


async def send_error(websocket, message: str):
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


async def send_to_robots(payload, robot_id: Optional[str] = None) -> int:
    sent_count = 0

    for websocket, robot_data in list(robots.items()):
        if robot_id and robot_data.get("robot_id") != robot_id:
            continue

        ok = await safe_send(websocket, payload)
        if ok:
            sent_count += 1

    return sent_count


async def publish_mission_update(mission, robot_id=None, event_type="mission:updated", message=None):
    payload = {
        "type": event_type,
        "robot_id": robot_id,
        "mission_id": mission["id"],
        "status": mission["status"],
        "mission": mission,
        "message": message,
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
            "last_seen": now_ts(),
            "last_seen_iso": now(),
            "active_mission_id": payload.get("mission_id"),
        }

        await broadcast_to_dashboards(
            {
                "type": "robot.connected",
                "robot_id": robot_id,
                "timestamp": now(),
            }
        )

        for mission in get_active_missions():
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

        robot_payload = {
            "type": "mission:assigned",
            "robot_id": robot_id,
            "mission_id": mission_id,
            "mission": mission,
            "timestamp": now(),
        }
        sent_count = await send_to_robots(robot_payload, robot_id)

        await publish_mission_update(
            mission,
            robot_id=robot_id,
            event_type="mission:assigned",
            message=f"Mission #{mission_id} envoyée à {sent_count} robot(s)",
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
        robots[websocket]["last_seen"] = now_ts()
        robots[websocket]["last_seen_iso"] = now()

    if event_type == "robot.heartbeat":
        if websocket in robots:
            robots[websocket]["active_mission_id"] = payload.get("mission_id") or robots[websocket].get("active_mission_id")

        await broadcast_to_dashboards(
            {
                "type": "robot.heartbeat",
                "robot_id": robot_id,
                "mission_id": payload.get("mission_id"),
                "timestamp": now(),
            }
        )
        return

    if event_type in {"robot:position", "robot.position_updated"}:
        mission_id = to_int(payload.get("mission_id"))
        x = to_float(payload.get("x"))
        y = to_float(payload.get("y"))

        if x is None or y is None:
            await send_error(websocket, "x and y required")
            return

        insert_robot_log(mission_id, x, y, robot_id=robot_id, status="POSITION")

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

    if event_type in {"mission:updated", "mission.status_updated", "mission:completed", "mission.completed"}:
        mission_id = to_int(payload.get("mission_id"))
        target_status = "COMPLETED" if event_type in {"mission:completed", "mission.completed"} else payload.get("status")

        if mission_id is None or not target_status:
            await send_error(websocket, "mission_id and status required")
            return

        if target_status not in ALLOWED_STATUSES:
            await send_error(websocket, f"invalid status: {target_status}")
            return

        mission, error = transition_mission(mission_id, target_status, payload.get("error_reason"))
        if error:
            await send_error(websocket, error)
            return

        insert_robot_log(
            mission_id=mission_id,
            x=payload.get("x"),
            y=payload.get("y"),
            robot_id=robot_id,
            status=mission["status"],
            message=payload.get("message") or payload.get("error_reason"),
        )

        if websocket in robots:
            robots[websocket]["active_mission_id"] = None if mission["status"] in TERMINAL_STATUSES else mission_id

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
            mission, _ = transition_mission(mission_id, "ERROR", reason)
            insert_robot_log(mission_id=mission_id, robot_id=robot_id, status="ERROR", message=reason)

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
        await publish_mission_update(mission, robot_id=robot_id, message=reason)


async def heartbeat_watchdog():
    while True:
        await asyncio.sleep(HEARTBEAT_WATCH_INTERVAL_SECONDS)
        threshold = now_ts() - HEARTBEAT_TIMEOUT_SECONDS
        for websocket, robot in list(robots.items()):
            if robot.get("last_seen", 0) >= threshold:
                continue

            robot_id = robot.get("robot_id")
            mission_id = to_int(robot.get("active_mission_id"))
            reason = f"Heartbeat timeout > {HEARTBEAT_TIMEOUT_SECONDS}s"
            mission = None

            if mission_id is not None:
                current_mission = get_mission(mission_id)
                if current_mission and current_mission["status"] not in TERMINAL_STATUSES:
                    mission, _ = transition_mission(mission_id, "ERROR", reason)
                    insert_robot_log(mission_id=mission_id, robot_id=robot_id, status="ERROR", message=reason)

            await broadcast_to_dashboards(
                {
                    "type": "robot.timeout",
                    "robot_id": robot_id,
                    "mission_id": mission_id,
                    "mission": mission,
                    "message": reason,
                    "timestamp": now(),
                }
            )
            await cleanup(websocket)


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
    watchdog_task = asyncio.create_task(heartbeat_watchdog())
    async with websockets.serve(handler, WS_HOST, WS_PORT, ping_interval=20, ping_timeout=20):
        print(f"RAA realtime server listening on ws://{WS_HOST}:{WS_PORT}")
        await asyncio.Future()
    watchdog_task.cancel()


if __name__ == "__main__":
    asyncio.run(main())
