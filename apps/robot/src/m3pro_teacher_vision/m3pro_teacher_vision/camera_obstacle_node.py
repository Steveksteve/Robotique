#!/usr/bin/env python3
"""
Visual obstacle detection using the depth camera.

Converts the depth image into a virtual LaserScan that Nav2 can use in
its costmap. This catches obstacles the 2D lidar misses — small floor
objects, transparent surfaces, objects below/above lidar height.

The node scans horizontal bands of the depth image and publishes the
nearest distance at each angular column as a LaserScan on
/teacher/camera_scan. Nav2 treats this exactly like a real lidar.

It also publishes an annotated image showing detected obstacles and
obstacle positions as PoseArray for the pick-and-place system.

Published topics:
  /teacher/camera_scan       - sensor_msgs/LaserScan  (virtual scan for Nav2)
  /teacher/camera_obstacles  - geometry_msgs/PoseArray (3D positions)
  /teacher/camera_obs_image  - sensor_msgs/Image       (annotated view)
"""
import math
from typing import Optional

import cv2
import numpy as np
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Pose, PoseArray
from sensor_msgs.msg import Image, LaserScan
from std_msgs.msg import Header


class CameraObstacleNode(Node):
    def __init__(self):
        super().__init__("camera_obstacle_node")

        # --- Parameters ---
        self.depth_topic = self.declare_parameter(
            "depth_topic", "/camera/depth/image_raw"
        ).value
        self.color_topic = self.declare_parameter(
            "color_topic", "/camera/color/image_raw"
        ).value

        # Camera intrinsics (defaults for common depth cameras)
        self.fx = float(self.declare_parameter("camera_fx", 615.0).value)
        self.fy = float(self.declare_parameter("camera_fy", 615.0).value)
        self.cx = float(self.declare_parameter("camera_cx", 320.0).value)
        self.cy = float(self.declare_parameter("camera_cy", 240.0).value)
        self.depth_scale = float(self.declare_parameter("depth_scale", 0.001).value)

        # Detection thresholds
        self.min_range = float(self.declare_parameter("min_range", 0.15).value)
        self.max_range = float(self.declare_parameter("max_range", 2.0).value)
        self.scan_height_ratio = float(
            self.declare_parameter("scan_height_ratio", 0.4).value
        )  # fraction of image height to scan (bottom portion)
        self.obstacle_height_min = float(
            self.declare_parameter("obstacle_height_min", 0.02).value
        )  # minimum height above floor to count (meters)

        # --- State ---
        self.latest_depth: Optional[Image] = None
        self.latest_color: Optional[Image] = None

        # --- Subscribers ---
        self.create_subscription(Image, self.depth_topic, self.on_depth, 5)
        self.create_subscription(Image, self.color_topic, self.on_color, 5)

        # --- Publishers ---
        self.scan_pub = self.create_publisher(
            LaserScan, "/teacher/camera_scan", 10
        )
        self.obstacle_pub = self.create_publisher(
            PoseArray, "/teacher/camera_obstacles", 10
        )
        self.image_pub = self.create_publisher(
            Image, "/teacher/camera_obs_image", 5
        )

        # --- Timer (5 Hz — depth processing is heavier than color) ---
        self.create_timer(0.2, self.process)

        self.get_logger().info(
            f"Camera obstacle detector started — depth={self.depth_topic}"
        )

    def on_depth(self, msg: Image):
        self.latest_depth = msg

    def on_color(self, msg: Image):
        self.latest_color = msg

    def process(self):
        if self.latest_depth is None:
            return

        depth_msg = self.latest_depth
        h, w = depth_msg.height, depth_msg.width
        encoding = depth_msg.encoding.lower()
        data = bytes(depth_msg.data)

        # Decode depth image to float meters
        if encoding in ("16uc1", "mono16"):
            raw = np.frombuffer(data, dtype=np.uint16).reshape(h, w)
            depth_m = raw.astype(np.float32) * self.depth_scale
        elif encoding in ("32fc1",):
            depth_m = np.frombuffer(data, dtype=np.float32).reshape(h, w)
        else:
            self.get_logger().warning(
                f"Unsupported depth encoding: {depth_msg.encoding}",
                throttle_duration_sec=5.0,
            )
            return

        # --- Build virtual laser scan from depth image ---
        # Scan the bottom portion of the image (where floor obstacles are)
        y_start = int(h * (1.0 - self.scan_height_ratio))
        y_end = h
        roi = depth_m[y_start:y_end, :]

        # For each column, find the minimum valid depth
        # This gives us the nearest obstacle at each horizontal angle
        col_min = np.full(w, self.max_range, dtype=np.float32)
        for x in range(w):
            col = roi[:, x]
            valid = col[(col > self.min_range) & (col < self.max_range)]
            if valid.size > 0:
                col_min[x] = float(np.min(valid))

        # Convert pixel columns to angles
        # Camera optical frame: X-right, Y-down, Z-forward
        angles = np.arctan2(np.arange(w, dtype=np.float32) - self.cx, self.fx)
        angle_min = float(angles[0])
        angle_max = float(angles[-1])
        angle_increment = float((angle_max - angle_min) / max(w - 1, 1))

        # Build LaserScan (in camera_color_optical_frame)
        # Note: we reverse so scan goes from right to left (ROS convention)
        scan = LaserScan()
        scan.header.stamp = depth_msg.header.stamp
        scan.header.frame_id = "camera_color_optical_frame"
        scan.angle_min = angle_min
        scan.angle_max = angle_max
        scan.angle_increment = angle_increment
        scan.time_increment = 0.0
        scan.scan_time = 0.2
        scan.range_min = self.min_range
        scan.range_max = self.max_range
        scan.ranges = col_min.tolist()
        self.scan_pub.publish(scan)

        # --- Find individual obstacles (clusters of close pixels) ---
        obstacle_mask = col_min < (self.max_range * 0.9)
        obstacles = []
        in_obstacle = False
        start_x = 0

        for x in range(w):
            if obstacle_mask[x] and not in_obstacle:
                start_x = x
                in_obstacle = True
            elif not obstacle_mask[x] and in_obstacle:
                # End of obstacle cluster
                mid_x = (start_x + x) // 2
                z = float(col_min[mid_x])
                px = (mid_x - self.cx) / self.fx * z
                # Estimate Y from the scan band midpoint
                mid_y = (y_start + y_end) // 2
                py = (mid_y - self.cy) / self.fy * z
                if z > self.min_range:
                    obstacles.append((px, py, z, start_x, x))
                in_obstacle = False

        if in_obstacle:
            mid_x = (start_x + w) // 2
            z = float(col_min[mid_x])
            px = (mid_x - self.cx) / self.fx * z
            mid_y = (y_start + y_end) // 2
            py = (mid_y - self.cy) / self.fy * z
            if z > self.min_range:
                obstacles.append((px, py, z, start_x, w))

        # Publish obstacle positions
        header = Header()
        header.stamp = depth_msg.header.stamp
        header.frame_id = "camera_color_optical_frame"

        pose_array = PoseArray()
        pose_array.header = header
        for px, py, pz, _, _ in obstacles:
            pose = Pose()
            pose.position.x = float(px)
            pose.position.y = float(py)
            pose.position.z = float(pz)
            pose.orientation.w = 1.0
            pose_array.poses.append(pose)
        self.obstacle_pub.publish(pose_array)

        # --- Annotated image ---
        if self.latest_color is not None:
            self.publish_annotated(obstacles, y_start, y_end, header)

        if obstacles:
            nearest = min(obstacles, key=lambda o: o[2])
            self.get_logger().info(
                f"Camera sees {len(obstacles)} obstacle(s), "
                f"nearest at {nearest[2]:.2f}m",
                throttle_duration_sec=2.0,
            )

    def publish_annotated(self, obstacles, y_start, y_end, header):
        msg = self.latest_color
        h, w = msg.height, msg.width
        encoding = msg.encoding.lower()
        data = bytes(msg.data)

        if encoding == "rgb8":
            arr = np.frombuffer(data, dtype=np.uint8).reshape(h, w, 3).copy()
        elif encoding == "bgr8":
            arr = np.frombuffer(data, dtype=np.uint8).reshape(h, w, 3).copy()
            arr = cv2.cvtColor(arr, cv2.COLOR_BGR2RGB)
        else:
            return

        # Draw scan band
        cv2.line(arr, (0, y_start), (w, y_start), (0, 255, 255), 1)

        # Draw obstacle bounding boxes
        for px, py, pz, x1, x2 in obstacles:
            cv2.rectangle(arr, (x1, y_start), (x2, h), (255, 0, 0), 2)
            label = f"{pz:.2f}m"
            cv2.putText(
                arr, label, (x1, y_start - 5),
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 1,
            )

        out = Image()
        out.header = header
        out.height, out.width = arr.shape[:2]
        out.encoding = "rgb8"
        out.step = out.width * 3
        out.data = arr.tobytes()
        self.image_pub.publish(out)


def main():
    rclpy.init()
    node = CameraObstacleNode()
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
