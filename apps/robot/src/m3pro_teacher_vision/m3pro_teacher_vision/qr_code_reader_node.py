#!/usr/bin/env python3

import time
import numpy as np

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from std_srvs.srv import Trigger
from sensor_msgs.msg import CompressedImage

import cv2
from pyzbar.pyzbar import decode as zbar_decode


class QrCodeReaderNode(Node):
    def __init__(self):
        super().__init__("qr_code_reader_node")

        self.camera_topic = self.declare_parameter(
            "camera_topic",
            "/camera/color/image_raw/compressed"
        ).value

        self.qr_topic = self.declare_parameter("qr_topic", "/qr_code").value
        self.min_publish_interval = float(
            self.declare_parameter("min_publish_interval", 0.5).value
        )

        self.last_qr = ""
        self.last_seen_at = 0.0
        self.last_publish_at = 0.0

        self.qr_pub = self.create_publisher(String, self.qr_topic, 10)
        self.create_service(Trigger, "/qr/read", self.read_qr_cb)

        self.create_subscription(
            CompressedImage,
            self.camera_topic,
            self.image_cb,
            10
        )

        self.get_logger().info("Decodeur QR pyzbar actif.")
        self.get_logger().info(
            f"QR reader ready: camera={self.camera_topic}, output={self.qr_topic}, service=/qr/read"
        )

    def image_cb(self, msg):
        now = time.time()

        if now - self.last_publish_at < self.min_publish_interval:
            return

        try:
            np_arr = np.frombuffer(msg.data, np.uint8)
            frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

            if frame is None:
                return

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            decoded = zbar_decode(gray)

            if not decoded:
                return

            data = decoded[0].data.decode("utf-8").strip()

        except Exception as exc:
            self.get_logger().warning(
                f"QR decode failed: {exc}",
                throttle_duration_sec=2.0
            )
            return

        if not data:
            return

        self.last_qr = data
        self.last_seen_at = now
        self.last_publish_at = now

        out = String()
        out.data = self.last_qr
        self.qr_pub.publish(out)

        self.get_logger().info(f"QR detected: {self.last_qr}")

    def read_qr_cb(self, request, response):
        if self.last_qr:
            response.success = True
            response.message = self.last_qr
        else:
            response.success = False
            response.message = "No QR code detected yet"

        return response


def main():
    rclpy.init()
    node = QrCodeReaderNode()

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
