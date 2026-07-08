#!/usr/bin/env python3
import math
from typing import List

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState

try:
    from arm_msgs.msg import ArmJoints
except ModuleNotFoundError:
    ArmJoints = None


JOINT_NAMES = [
    "base_yaw_joint",
    "shoulder_joint",
    "elbow_joint",
    "wrist_pitch_joint",
    "wrist_roll_joint",
    "left_finger_joint",
    "right_finger_joint",
]


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def deg_to_rad_centered(degrees: float, center: float = 90.0) -> float:
    return math.radians(float(degrees) - center)


class ArmJointStateBridgeDemo(Node):
    """Bridge Yahboom /arm6_joints messages to standard /joint_states."""

    def __init__(self) -> None:
        super().__init__("arm_joint_state_bridge_demo")
        self.demo_motion = bool(self.declare_parameter("demo_motion", False).value)
        self.publish_rate_hz = float(self.declare_parameter("publish_rate_hz", 20.0).value)
        self.arm_topic = self.declare_parameter("arm_topic", "/arm6_joints").value
        self.joint_states_topic = self.declare_parameter("joint_states_topic", "/teacher/joint_states").value

        self.joint_pub = self.create_publisher(JointState, self.joint_states_topic, 10)
        self.last_positions = self.home_positions()
        self.last_real_msg_time = None
        self.start_time = self.get_clock().now()

        if ArmJoints is not None:
            self.create_subscription(ArmJoints, self.arm_topic, self.on_arm_joints, 10)
        else:
            self.get_logger().warning("arm_msgs is not available; publishing demo joint states only")

        self.timer = self.create_timer(1.0 / self.publish_rate_hz, self.on_timer)
        self.get_logger().info(f"URDF joint bridge publishing {self.joint_states_topic}")

    def home_positions(self) -> List[float]:
        return [
            0.0,
            math.radians(30.0),
            math.radians(-80.0),
            math.radians(-70.0),
            0.0,
            0.02,
            0.02,
        ]

    def on_arm_joints(self, msg) -> None:
        joint1 = getattr(msg, "joint1", 90)
        joint2 = getattr(msg, "joint2", 120)
        joint3 = getattr(msg, "joint3", 10)
        joint4 = getattr(msg, "joint4", 20)
        joint5 = getattr(msg, "joint5", 90)
        joint6 = getattr(msg, "joint6", 60)

        gripper_open_m = clamp((90.0 - float(joint6)) / 60.0 * 0.04, 0.0, 0.04)
        self.last_positions = [
            clamp(deg_to_rad_centered(joint1, 90.0), -1.57, 1.57),
            clamp(deg_to_rad_centered(joint2, 90.0), -1.57, 1.57),
            clamp(deg_to_rad_centered(joint3, 90.0), -1.57, 1.57),
            clamp(deg_to_rad_centered(joint4, 90.0), -1.57, 1.57),
            clamp(deg_to_rad_centered(joint5, 90.0), -1.57, 1.57),
            gripper_open_m,
            gripper_open_m,
        ]
        self.last_real_msg_time = self.get_clock().now()

    def demo_positions(self) -> List[float]:
        elapsed = (self.get_clock().now() - self.start_time).nanoseconds / 1e9
        return [
            0.45 * math.sin(elapsed * 0.7),
            0.45 + 0.2 * math.sin(elapsed * 0.9),
            -0.8 + 0.2 * math.sin(elapsed * 1.1),
            -0.7 + 0.25 * math.sin(elapsed * 1.3),
            0.5 * math.sin(elapsed * 1.5),
            0.02 + 0.018 * math.sin(elapsed * 2.0),
            0.02 + 0.018 * math.sin(elapsed * 2.0),
        ]

    def on_timer(self) -> None:
        positions = self.last_positions
        if self.demo_motion and self.last_real_msg_time is None:
            positions = self.demo_positions()

        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = JOINT_NAMES
        msg.position = positions
        self.joint_pub.publish(msg)


def main() -> None:
    rclpy.init()
    node = ArmJointStateBridgeDemo()
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
