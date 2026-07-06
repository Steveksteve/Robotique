#!/usr/bin/env python3
"""
Object detector using OpenCV color-based (HSV) detection + depth camera.

Subscribes to RGB + depth images, detects objects matching the target HSV
range, computes their 3D position using depth + camera intrinsics, and
publishes detection results.

Published topics:
  /teacher/detections        - geometry_msgs/PoseArray (3D positions in camera frame)
  /teacher/detection_markers - visualization_msgs/MarkerArray (for RViz)
  /teacher/detection_image   - sensor_msgs/Image (annotated camera image)
"""
import math
from typing import List, Tuple

import cv2
import numpy as np
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Pose, PoseArray
from sensor_msgs.msg import Image
from std_msgs.msg import Header
from visualization_msgs.msg import Marker, MarkerArray


class ObjectDetectorNode(Node):
    def __init__(self):
        super().__init__("object_detector_node")

        # --- Parameters ---
        self.color_topic = self.declare_parameter("color_topic", "/camera/color/image_raw").value
        self.depth_topic = self.declare_parameter("depth_topic", "/camera/depth/image_raw").value

        self.hsv_low_1 = self.declare_parameter("hsv_low_1", [0, 120, 70]).value
        self.hsv_high_1 = self.declare_parameter("hsv_high_1", [10, 255, 255]).value
        self.hsv_low_2 = self.declare_parameter("hsv_low_2", [170, 120, 70]).value
        self.hsv_high_2 = self.declare_parameter("hsv_high_2", [180, 255, 255]).value

        self.min_area = int(self.declare_parameter("min_contour_area", 500).value)
        self.max_depth = float(self.declare_parameter("max_detection_depth", 1.0).value)
        self.min_depth = float(self.declare_parameter("min_detection_depth", 0.15).value)

        self.fx = float(self.declare_parameter("camera_fx", 615.0).value)
        self.fy = float(self.declare_parameter("camera_fy", 615.0).value)
        self.cx = float(self.declare_parameter("camera_cx", 320.0).value)
        self.cy = float(self.declare_parameter("camera_cy", 240.0).value)
        self.depth_scale = float(self.declare_parameter("depth_scale", 0.001).value)

        # --- State ---
        self.latest_color = None
        self.latest_depth = None

        # --- Subscribers ---
        self.create_subscription(Image, self.color_topic, self.on_color, 5)
        self.create_subscription(Image, self.depth_topic, self.on_depth, 5)

        # --- Publishers ---
        self.pose_pub = self.create_publisher(PoseArray, "/teacher/detections", 10)
        self.marker_pub = self.create_publisher(MarkerArray, "/teacher/detection_markers", 10)
        self.image_pub = self.create_publisher(Image, "/teacher/detection_image", 5)

        # --- Detection timer (10 Hz) ---
        self.create_timer(0.1, self.detect)
        self.get_logger().info(
            f"Object detector started -- color={self.color_topic} depth={self.depth_topic}"
        )

    def on_color(self, msg: Image):
        self.latest_color = msg

    def on_depth(self, msg: Image):
        self.latest_depth = msg

    def decode_image(self, msg: Image) -> np.ndarray:
        """Convert ROS Image to numpy array."""
        h, w = msg.height, msg.width
        encoding = msg.encoding.lower()
        data = bytes(msg.data)

        if encoding == "rgb8":
            return np.frombuffer(data, dtype=np.uint8).reshape(h, w, 3)
        elif encoding == "bgr8":
            arr = np.frombuffer(data, dtype=np.uint8).reshape(h, w, 3)
            return cv2.cvtColor(arr, cv2.COLOR_BGR2RGB)
        elif encoding in ("16uc1", "mono16"):
            return np.frombuffer(data, dtype=np.uint16).reshape(h, w)
        elif encoding in ("32fc1",):
            return np.frombuffer(data, dtype=np.float32).reshape(h, w)
        elif encoding in ("mono8", "8uc1"):
            return np.frombuffer(data, dtype=np.uint8).reshape(h, w)
        else:
            self.get_logger().warning(f"Unsupported encoding: {msg.encoding}")
            return np.zeros((h, w, 3), dtype=np.uint8)

    def detect(self):
        if self.latest_color is None:
            return

        color_img = self.decode_image(self.latest_color)
        hsv = cv2.cvtColor(color_img, cv2.COLOR_RGB2HSV)

        # Create mask from two HSV ranges (handles red hue wrapping)
        mask1 = cv2.inRange(
            hsv,
            np.array(self.hsv_low_1, dtype=np.uint8),
            np.array(self.hsv_high_1, dtype=np.uint8),
        )
        mask2 = cv2.inRange(
            hsv,
            np.array(self.hsv_low_2, dtype=np.uint8),
            np.array(self.hsv_high_2, dtype=np.uint8),
        )
        mask = cv2.bitwise_or(mask1, mask2)

        # Clean up mask
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Get depth image if available
        depth_img = None
        if self.latest_depth is not None:
            depth_img = self.decode_image(self.latest_depth)

        detections: List[Tuple[float, float, float, int, int, int]] = []

        for contour in contours:
            area = cv2.contourArea(contour)
            if area < self.min_area:
                continue

            # Bounding circle for centroid
            (cx_px, cy_px), radius = cv2.minEnclosingCircle(contour)
            cx_px, cy_px = int(cx_px), int(cy_px)

            # Get depth at centroid
            z = 0.0
            if depth_img is not None and 0 <= cy_px < depth_img.shape[0] and 0 <= cx_px < depth_img.shape[1]:
                # Sample a small region around centroid for robustness
                r = max(1, int(radius * 0.3))
                y1 = max(0, cy_px - r)
                y2 = min(depth_img.shape[0], cy_px + r)
                x1 = max(0, cx_px - r)
                x2 = min(depth_img.shape[1], cx_px + r)
                region = depth_img[y1:y2, x1:x2].astype(np.float64)

                if depth_img.dtype == np.uint16:
                    region = region * self.depth_scale
                # Use median to reject outliers
                valid = region[(region > self.min_depth) & (region < self.max_depth)]
                if valid.size > 0:
                    z = float(np.median(valid))

            if z < self.min_depth or z > self.max_depth:
                # No valid depth -- still report 2D detection but with z=0
                z = 0.0

            # Back-project to 3D (camera optical frame)
            x_3d = (cx_px - self.cx) / self.fx * z if z > 0 else 0.0
            y_3d = (cy_px - self.cy) / self.fy * z if z > 0 else 0.0

            detections.append((x_3d, y_3d, z, cx_px, cy_px, int(radius)))

        # Publish PoseArray
        header = Header()
        header.stamp = self.get_clock().now().to_msg()
        header.frame_id = "camera_color_optical_frame"

        pose_array = PoseArray()
        pose_array.header = header
        for x, y, z, _, _, _ in detections:
            pose = Pose()
            pose.position.x = x
            pose.position.y = y
            pose.position.z = z
            pose.orientation.w = 1.0
            pose_array.poses.append(pose)
        self.pose_pub.publish(pose_array)

        # Publish RViz markers
        self.publish_markers(header, detections)

        # Publish annotated image
        self.publish_annotated_image(color_img, detections, header)

        if detections:
            best = min(detections, key=lambda d: d[2] if d[2] > 0 else 999)
            self.get_logger().info(
                f"Detected {len(detections)} object(s), nearest at "
                f"({best[0]:.2f}, {best[1]:.2f}, {best[2]:.2f})m",
                throttle_duration_sec=1.0,
            )

    def publish_markers(self, header, detections):
        markers = MarkerArray()
        for i, (x, y, z, _, _, _) in enumerate(detections):
            if z <= 0:
                continue
            m = Marker()
            m.header = header
            m.ns = "detections"
            m.id = i
            m.type = Marker.SPHERE
            m.action = Marker.ADD
            m.pose.position.x = x
            m.pose.position.y = y
            m.pose.position.z = z
            m.pose.orientation.w = 1.0
            m.scale.x = m.scale.y = m.scale.z = 0.05
            m.color.r = 1.0
            m.color.g = 0.2
            m.color.a = 0.9
            m.lifetime.sec = 0
            m.lifetime.nanosec = 500_000_000
            markers.markers.append(m)

        # Delete old markers
        delete = Marker()
        delete.header = header
        delete.ns = "detections"
        delete.action = Marker.DELETEALL
        if not markers.markers:
            markers.markers.append(delete)

        self.marker_pub.publish(markers)

    def publish_annotated_image(self, color_img, detections, header):
        annotated = color_img.copy()
        for x, y, z, cx, cy, r in detections:
            color = (0, 255, 0) if z > 0 else (255, 255, 0)
            cv2.circle(annotated, (cx, cy), r, color, 2)
            label = f"{z:.2f}m" if z > 0 else "no depth"
            cv2.putText(annotated, label, (cx - 30, cy - r - 8),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        msg = Image()
        msg.header = header
        msg.height, msg.width = annotated.shape[:2]
        msg.encoding = "rgb8"
        msg.step = msg.width * 3
        msg.data = annotated.tobytes()
        self.image_pub.publish(msg)


def main():
    rclpy.init()
    node = ObjectDetectorNode()
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
