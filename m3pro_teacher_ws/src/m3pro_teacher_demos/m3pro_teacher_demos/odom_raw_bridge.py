#!/usr/bin/env python3
"""Bridge Yahboom /odom_raw to the standard /odom topic and TF tree."""

import rclpy
from geometry_msgs.msg import TransformStamped
from nav_msgs.msg import Odometry
from rclpy.node import Node
from tf2_ros import TransformBroadcaster


class OdomRawBridge(Node):
    def __init__(self) -> None:
        super().__init__("odom_raw_bridge")

        self.input_topic = self.declare_parameter("input_topic", "/odom_raw").value
        self.output_topic = self.declare_parameter("output_topic", "/odom").value
        self.odom_frame = self.declare_parameter("odom_frame", "odom").value
        self.base_frame = self.declare_parameter("base_frame", "base_footprint").value
        self.publish_tf = bool(self.declare_parameter("publish_tf", True).value)

        self.odom_pub = self.create_publisher(Odometry, self.output_topic, 20)
        self.tf_broadcaster = TransformBroadcaster(self)
        self.create_subscription(Odometry, self.input_topic, self.on_odom, 20)

        self.get_logger().info(
            f"Bridging {self.input_topic} -> {self.output_topic}, "
            f"TF {self.odom_frame} -> {self.base_frame}"
        )

    def on_odom(self, msg: Odometry) -> None:
        out = Odometry()
        out.header = msg.header
        out.header.frame_id = self.odom_frame
        out.child_frame_id = self.base_frame
        out.pose = msg.pose
        out.twist = msg.twist
        self.odom_pub.publish(out)

        if not self.publish_tf:
            return

        tf = TransformStamped()
        tf.header = out.header
        tf.child_frame_id = out.child_frame_id
        tf.transform.translation.x = out.pose.pose.position.x
        tf.transform.translation.y = out.pose.pose.position.y
        tf.transform.translation.z = out.pose.pose.position.z
        tf.transform.rotation = out.pose.pose.orientation
        self.tf_broadcaster.sendTransform(tf)


def main() -> None:
    rclpy.init()
    node = OdomRawBridge()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
