#!/usr/bin/env python3
import math
from typing import Tuple

import rclpy
from geometry_msgs.msg import TransformStamped
from rclpy.node import Node
from std_msgs.msg import String
from tf2_ros import StaticTransformBroadcaster, TransformBroadcaster


def quaternion_from_euler(roll: float, pitch: float, yaw: float) -> Tuple[float, float, float, float]:
    cr = math.cos(roll * 0.5)
    sr = math.sin(roll * 0.5)
    cp = math.cos(pitch * 0.5)
    sp = math.sin(pitch * 0.5)
    cy = math.cos(yaw * 0.5)
    sy = math.sin(yaw * 0.5)

    return (
        sr * cp * cy - cr * sp * sy,
        cr * sp * cy + sr * cp * sy,
        cr * cp * sy - sr * sp * cy,
        cr * cp * cy + sr * sp * sy,
    )


def make_transform(
    stamp,
    parent: str,
    child: str,
    xyz: Tuple[float, float, float],
    rpy: Tuple[float, float, float],
) -> TransformStamped:
    msg = TransformStamped()
    msg.header.stamp = stamp
    msg.header.frame_id = parent
    msg.child_frame_id = child
    msg.transform.translation.x = float(xyz[0])
    msg.transform.translation.y = float(xyz[1])
    msg.transform.translation.z = float(xyz[2])
    qx, qy, qz, qw = quaternion_from_euler(*rpy)
    msg.transform.rotation.x = qx
    msg.transform.rotation.y = qy
    msg.transform.rotation.z = qz
    msg.transform.rotation.w = qw
    return msg


class Tf2SensorFramesDemo(Node):
    """Publish simple teaching transforms for the robot body, lidars, and camera."""

    def __init__(self) -> None:
        super().__init__("tf2_sensor_frames_demo")
        self.base_frame = self.declare_parameter("base_frame", "base_link").value
        self.odom_frame = self.declare_parameter("odom_frame", "teacher_odom").value
        self.publish_odom = bool(self.declare_parameter("publish_odom", False).value)

        self.static_broadcaster = StaticTransformBroadcaster(self)
        self.dynamic_broadcaster = TransformBroadcaster(self)
        self.status_pub = self.create_publisher(String, "/teacher/tf2_status", 10)

        self.publish_static_frames()
        self.timer = self.create_timer(0.25, self.on_timer)
        self.start_time = self.get_clock().now()

        self.get_logger().info("TF2 demo started.")
        self.get_logger().info("Try: ros2 run tf2_ros tf2_echo base_link scan0_frame")
        self.get_logger().info("Try: ros2 run tf2_ros tf2_echo base_link camera_color_optical_frame")

    def publish_static_frames(self) -> None:
        now = self.get_clock().now().to_msg()
        pi = math.pi
        transforms = [
            make_transform(now, self.base_frame, "scan0_frame", (0.17, 0.0, 0.11), (0.0, 0.0, 0.0)),
            make_transform(now, self.base_frame, "scan1_frame", (-0.17, 0.0, 0.11), (0.0, 0.0, pi)),
            make_transform(now, self.base_frame, "camera_link", (0.18, 0.0, 0.23), (0.0, 0.0, 0.0)),
            make_transform(now, "camera_link", "camera_color_optical_frame", (0.025, 0.0, 0.0), (-pi / 2.0, 0.0, -pi / 2.0)),
            make_transform(now, self.base_frame, "arm_base_link", (0.02, 0.0, 0.105), (0.0, 0.0, 0.0)),
        ]
        self.static_broadcaster.sendTransform(transforms)

    def on_timer(self) -> None:
        if self.publish_odom:
            elapsed = (self.get_clock().now() - self.start_time).nanoseconds / 1e9
            yaw = 0.35 * math.sin(elapsed * 0.35)
            tf = make_transform(
                self.get_clock().now().to_msg(),
                self.odom_frame,
                self.base_frame,
                (0.25 * math.sin(elapsed * 0.2), 0.0, 0.0),
                (0.0, 0.0, yaw),
            )
            self.dynamic_broadcaster.sendTransform(tf)

        status = String()
        status.data = (
            "frames: base_link -> scan0_frame, scan1_frame, camera_link, "
            "camera_link -> camera_color_optical_frame"
        )
        self.status_pub.publish(status)


def main() -> None:
    rclpy.init()
    node = Tf2SensorFramesDemo()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        try:
            node.destroy_node()
        except KeyboardInterrupt:
            pass
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
