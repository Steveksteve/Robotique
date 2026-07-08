#!/usr/bin/env python3
"""
Mission executor for the RAA MVP.

It polls the web API, takes a CREATED/ASSIGNED mission, then executes:
ASSIGNED -> NAVIGATING_TO_PICKUP -> SCANNING_QR -> PICKING_UP
-> NAVIGATING_TO_DROP -> DROPPING_OFF -> COMPLETED.

In real mode it sends Nav2 goals. In dry_run mode it only waits and updates the API.
"""

import json
import math
import threading
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any, Dict, Optional

try:
    import websocket
    HAS_WEBSOCKET = True
except ImportError:
    websocket = None
    HAS_WEBSOCKET = False

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from geometry_msgs.msg import PoseStamped
from std_srvs.srv import Trigger

try:
    from nav2_msgs.action import NavigateToPose
    HAS_NAV2 = True
except ImportError:
    NavigateToPose = None
    HAS_NAV2 = False

try:
    from m3pro_teacher_interfaces.srv import Home, SetJoints
    HAS_ARM_SERVICES = True
except ImportError:
    Home = None
    SetJoints = None
    HAS_ARM_SERVICES = False


@dataclass
class MapPoint:
    x: float
    y: float
    theta: float


def yaw_to_quaternion(theta: float):
    half = theta / 2.0
    return 0.0, 0.0, math.sin(half), math.cos(half)


class RobotRealtimeBridge:
    """Best-effort WebSocket bridge used to mirror API status updates to the dashboard."""

    def __init__(self, ws_url: str, robot_id: str, logger):
        self.ws_url = (ws_url or "").strip()
        self.robot_id = robot_id
        self.logger = logger
        self.connection = None
        self.connected = False
        self.stop_event = threading.Event()
        self.lock = threading.Lock()
        self.thread = None
        self.active_mission_id = None

    def start(self):
        if not self.ws_url:
            return
        if not HAS_WEBSOCKET:
            self.logger.warning("websocket-client unavailable: realtime bridge disabled")
            return
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def _run(self):
        while not self.stop_event.is_set():
            try:
                self.connection = websocket.create_connection(self.ws_url, timeout=5)
                self.connected = True
                self.send({
                    "type": "identify",
                    "client_type": "robot",
                    "robot_id": self.robot_id,
                    "mission_id": self.active_mission_id,
                })
                self.logger.info(f"Realtime bridge connected: {self.ws_url}")
                while not self.stop_event.is_set():
                    self.send({
                        "type": "robot.heartbeat",
                        "robot_id": self.robot_id,
                        "mission_id": self.active_mission_id,
                    })
                    time.sleep(5.0)
            except Exception as exc:
                self.connected = False
                self.logger.warning(f"Realtime bridge unavailable: {exc}")
                time.sleep(2.0)
            finally:
                with self.lock:
                    try:
                        if self.connection is not None:
                            self.connection.close()
                    except Exception:
                        pass
                    self.connection = None
                    self.connected = False

    def send(self, payload: Dict[str, Any]) -> bool:
        if not self.ws_url or not self.connected or self.connection is None:
            return False
        try:
            payload.setdefault("robot_id", self.robot_id)
            payload.setdefault("timestamp", datetime_utc_now())
            with self.lock:
                self.connection.send(json.dumps(payload))
            return True
        except Exception as exc:
            self.logger.warning(f"Realtime send failed: {exc}")
            self.connected = False
            return False

    def publish_status(self, mission_id: int, status: str, error_reason: Optional[str] = None):
        self.active_mission_id = None if status in {"COMPLETED", "ERROR"} else mission_id
        event_type = "mission:completed" if status == "COMPLETED" else "mission:updated"
        payload = {
            "type": event_type,
            "mission_id": mission_id,
            "status": status,
        }
        if error_reason:
            payload["error_reason"] = error_reason
        self.send(payload)

    def publish_position(self, mission_id: int, x: float, y: float):
        self.active_mission_id = mission_id
        self.send({
            "type": "robot:position",
            "mission_id": mission_id,
            "x": x,
            "y": y,
        })

    def stop(self):
        self.stop_event.set()
        with self.lock:
            try:
                if self.connection is not None:
                    self.connection.close()
            except Exception:
                pass


def datetime_utc_now() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()


class MissionExecutorNode(Node):
    def __init__(self):
        super().__init__("mission_executor_node")

        self.api_base = self.declare_parameter("api_base", "http://localhost:8000").value.rstrip("/")
        self.ws_url = self.declare_parameter("ws_url", "").value
        self.robot_id = self.declare_parameter("robot_id", "raa-robot-01").value
        self.poll_seconds = float(self.declare_parameter("poll_seconds", 2.0).value)
        self.dry_run = self.as_bool(self.declare_parameter("dry_run", True).value)
        self.simulated_qr = self.declare_parameter("simulated_qr", "a").value
        self.qr_timeout = float(self.declare_parameter("qr_timeout", 12.0).value)

        self.default_pickup = MapPoint(
            float(self.declare_parameter("pickup_x", 2.62).value),
            float(self.declare_parameter("pickup_y", 6.12).value),
            float(self.declare_parameter("pickup_theta", -1.90).value),
        )
        self.default_dropoff = MapPoint(
            float(self.declare_parameter("dropoff_x", 1.32).value),
            float(self.declare_parameter("dropoff_y", 2.18).value),
            float(self.declare_parameter("dropoff_theta", -1.90).value),
        )

        self.busy = False
        self.current_mission_id = None

        self.nav_client = None
        if HAS_NAV2:
            self.nav_client = ActionClient(self, NavigateToPose, "navigate_to_pose")
        elif not self.dry_run:
            self.get_logger().warning("nav2_msgs unavailable: forcing dry_run mode")
            self.dry_run = True

        self.qr_client = self.create_client(Trigger, "/qr/read")
        self.gripper_open_client = self.create_client(Trigger, "/arm/gripper_open")
        self.gripper_close_client = self.create_client(Trigger, "/arm/gripper_close")
        self.home_client = self.create_client(Home, "/arm/home") if HAS_ARM_SERVICES else None
        self.set_joints_client = self.create_client(SetJoints, "/arm/set_all_joints") if HAS_ARM_SERVICES else None

        self.realtime = RobotRealtimeBridge(self.ws_url, self.robot_id, self.get_logger())
        self.realtime.start()

        self.create_timer(self.poll_seconds, self.poll_once)
        self.get_logger().info(
            f"Mission executor ready: api={self.api_base}, ws={self.ws_url or 'disabled'}, dry_run={self.dry_run}, robot_id={self.robot_id}"
        )

    @staticmethod
    def as_bool(value) -> bool:
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return bool(value)
        if isinstance(value, str):
            return value.strip().lower() in {"1", "true", "yes", "on"}
        return False

    def wait_future(self, future, timeout_sec: float = 30.0):
        deadline = time.time() + timeout_sec
        while rclpy.ok() and not future.done() and time.time() < deadline:
            time.sleep(0.05)
        if not future.done():
            return None
        return future.result()

    # ---------- API ----------

    def api_request(self, method: str, path: str, payload: Optional[Dict[str, Any]] = None):
        url = f"{self.api_base}{path}"
        data = None
        headers = {"Content-Type": "application/json"}
        if payload is not None:
            data = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(request, timeout=5) as response:
                body = response.read().decode("utf-8")
                return json.loads(body) if body else None
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            self.get_logger().error(f"API {method} {path} failed: HTTP {exc.code} {body}")
            return None
        except Exception as exc:
            self.get_logger().error(f"API {method} {path} failed: {exc}")
            return None

    def get_missions(self):
        missions = self.api_request("GET", "/missions")
        return missions if isinstance(missions, list) else []

    def set_status(self, mission_id: int, status: str, error_reason: Optional[str] = None):
        payload: Dict[str, Any] = {"status": status, "robot_id": self.robot_id}
        if error_reason:
            payload["error_reason"] = error_reason
        self.get_logger().info(f"Mission #{mission_id} -> {status}")
        result = self.api_request("PATCH", f"/missions/{mission_id}/status", payload)
        if result is not None:
            self.realtime.publish_status(mission_id, status, error_reason)
        return result

    def publish_position(self, mission_id: int, point: MapPoint):
        self.realtime.publish_position(mission_id, point.x, point.y)

    # ---------- Mission loop ----------

    def poll_once(self):
        if self.busy:
            return

        missions = self.get_missions()
        next_mission = None
        for mission in sorted(missions, key=lambda item: int(item.get("id", 0))):
            if mission.get("status") in {"CREATED", "ASSIGNED"}:
                next_mission = mission
                break

        if not next_mission:
            return

        self.busy = True
        self.current_mission_id = int(next_mission["id"])
        thread = threading.Thread(
            target=self.execute_mission_thread,
            args=(next_mission,),
            daemon=True,
        )
        thread.start()

    def execute_mission_thread(self, mission: Dict[str, Any]):
        try:
            self.execute_mission(mission)
        finally:
            self.current_mission_id = None
            self.busy = False

    def execute_mission(self, mission: Dict[str, Any]):
        mission_id = int(mission["id"])
        expected_qr = str(mission.get("expected_qr") or "a")
        pickup = self.point_from_mission(mission, "pickup", self.default_pickup)
        dropoff = self.point_from_mission(mission, "dropoff", self.default_dropoff)

        if mission.get("status") == "CREATED":
            if self.set_status(mission_id, "ASSIGNED") is None:
                return

        if self.set_status(mission_id, "NAVIGATING_TO_PICKUP") is None:
            return
        if not self.navigate_to(pickup):
            self.set_status(mission_id, "ERROR", "Navigation vers le point A impossible")
            return
        self.publish_position(mission_id, pickup)

        if self.set_status(mission_id, "SCANNING_QR") is None:
            return
        detected_qr = self.read_qr()
        if detected_qr != expected_qr:
            self.set_status(
                mission_id,
                "ERROR",
                f"QR incorrect: attendu {expected_qr}, detecte {detected_qr or 'aucun'}",
            )
            return

        if self.set_status(mission_id, "PICKING_UP") is None:
            return
        if not self.pick_object():
            self.set_status(mission_id, "ERROR", "Echec prise objet")
            return

        if self.set_status(mission_id, "NAVIGATING_TO_DROP") is None:
            return
        if not self.navigate_to(dropoff):
            self.set_status(mission_id, "ERROR", "Navigation vers le point B impossible")
            return
        self.publish_position(mission_id, dropoff)

        if self.set_status(mission_id, "DROPPING_OFF") is None:
            return
        if not self.drop_object():
            self.set_status(mission_id, "ERROR", "Echec depot objet")
            return

        self.set_status(mission_id, "COMPLETED")

    def point_from_mission(self, mission: Dict[str, Any], prefix: str, default: MapPoint) -> MapPoint:
        try:
            return MapPoint(
                float(mission.get(f"{prefix}_x") or default.x),
                float(mission.get(f"{prefix}_y") or default.y),
                float(mission.get(f"{prefix}_theta") or default.theta),
            )
        except (TypeError, ValueError):
            return default

    # ---------- Nav2 ----------

    def navigate_to(self, point: MapPoint) -> bool:
        self.get_logger().info(f"Navigate to x={point.x:.2f}, y={point.y:.2f}, theta={point.theta:.2f}")
        if self.dry_run:
            time.sleep(2.0)
            return True

        if self.nav_client is None:
            return False

        if not self.nav_client.wait_for_server(timeout_sec=10.0):
            self.get_logger().error("Nav2 action server /navigate_to_pose unavailable")
            return False

        goal = NavigateToPose.Goal()
        goal.pose = PoseStamped()
        goal.pose.header.frame_id = "map"
        goal.pose.header.stamp = self.get_clock().now().to_msg()
        goal.pose.pose.position.x = point.x
        goal.pose.pose.position.y = point.y
        qx, qy, qz, qw = yaw_to_quaternion(point.theta)
        goal.pose.pose.orientation.x = qx
        goal.pose.pose.orientation.y = qy
        goal.pose.pose.orientation.z = qz
        goal.pose.pose.orientation.w = qw

        future = self.nav_client.send_goal_async(goal)
        handle = self.wait_future(future, timeout_sec=15.0)
        if not handle or not handle.accepted:
            self.get_logger().error("Nav2 goal rejected")
            return False

        result_future = handle.get_result_async()
        result = self.wait_future(result_future, timeout_sec=120.0)
        status = getattr(result, "status", None)
        self.get_logger().info(f"Nav2 result status={status}")
        return True

    # ---------- QR ----------

    def read_qr(self) -> str:
        if self.dry_run:
            self.get_logger().info(f"Dry-run QR detected: {self.simulated_qr}")
            return str(self.simulated_qr)

        deadline = time.time() + self.qr_timeout
        while time.time() < deadline:
            if not self.qr_client.wait_for_service(timeout_sec=1.0):
                self.get_logger().warning("/qr/read service unavailable", throttle_duration_sec=2.0)
                continue

            future = self.qr_client.call_async(Trigger.Request())
            response = self.wait_future(future, timeout_sec=2.0)
            if response and response.success:
                qr = response.message.strip()
                self.get_logger().info(f"QR read: {qr}")
                return qr
            time.sleep(0.5)
        return ""

    # ---------- Arm ----------

    def call_trigger(self, client, name: str) -> bool:
        if self.dry_run:
            self.get_logger().info(f"Dry-run arm service: {name}")
            time.sleep(0.5)
            return True
        if not client.wait_for_service(timeout_sec=5.0):
            self.get_logger().error(f"Service unavailable: {name}")
            return False
        future = client.call_async(Trigger.Request())
        response = self.wait_future(future, timeout_sec=5.0)
        return bool(response and response.success)

    def call_home(self) -> bool:
        if self.dry_run:
            self.get_logger().info("Dry-run arm service: /arm/home")
            time.sleep(0.5)
            return True
        if self.home_client is None or not self.home_client.wait_for_service(timeout_sec=5.0):
            self.get_logger().error("Service unavailable: /arm/home")
            return False
        future = self.home_client.call_async(Home.Request())
        response = self.wait_future(future, timeout_sec=5.0)
        return bool(response and response.success)

    def set_arm_pose(self, values) -> bool:
        if self.dry_run:
            self.get_logger().info(f"Dry-run arm pose: {values}")
            time.sleep(0.5)
            return True
        if self.set_joints_client is None or not self.set_joints_client.wait_for_service(timeout_sec=5.0):
            self.get_logger().error("Service unavailable: /arm/set_all_joints")
            return False
        request = SetJoints.Request()
        request.values = [float(v) for v in values]
        future = self.set_joints_client.call_async(request)
        response = self.wait_future(future, timeout_sec=5.0)
        return bool(response and response.success)

    def pick_object(self) -> bool:
        # Predefined safe sequence for MVP. Adjust after measuring the real object height.
        return (
            self.call_trigger(self.gripper_open_client, "/arm/gripper_open")
            and self.set_arm_pose([90.0, 105.0, 45.0, 35.0, 90.0, 30.0])
            and self.call_trigger(self.gripper_close_client, "/arm/gripper_close")
            and self.call_home()
        )

    def drop_object(self) -> bool:
        return (
            self.set_arm_pose([90.0, 105.0, 45.0, 35.0, 90.0, 75.0])
            and self.call_trigger(self.gripper_open_client, "/arm/gripper_open")
            and self.call_home()
        )


def main():
    rclpy.init()
    node = MissionExecutorNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.realtime.stop()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()