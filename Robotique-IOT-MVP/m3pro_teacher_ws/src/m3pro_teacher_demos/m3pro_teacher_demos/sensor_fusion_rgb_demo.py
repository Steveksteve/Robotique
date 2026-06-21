#!/usr/bin/env python3
import math
from typing import Dict, Iterable, List, Optional, Tuple

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, LaserScan
from std_msgs.msg import ColorRGBA, String, UInt16


def finite_ranges(scan: LaserScan) -> Iterable[Tuple[float, float]]:
    angle = float(scan.angle_min)
    step = float(scan.angle_increment)
    for value in scan.ranges:
        if math.isfinite(value) and scan.range_min <= value <= scan.range_max:
            yield angle, float(value)
        angle += step


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


class SensorFusionRgbDemo(Node):
    """Merge lidar scans, read simple camera color, and react through RGB."""

    def __init__(self) -> None:
        super().__init__("sensor_fusion_rgb_demo")
        self.simulate = bool(self.declare_parameter("simulate", False).value)
        self.base_frame = self.declare_parameter("base_frame", "base_link").value

        default_front = "/teacher/sim/scan0" if self.simulate else "/scan0"
        default_rear = "/teacher/sim/scan1" if self.simulate else "/scan1"
        default_camera = "/teacher/sim/camera" if self.simulate else "/camera/color/image_raw"

        self.front_scan_topic = self.declare_parameter("front_scan_topic", default_front).value
        self.rear_scan_topic = self.declare_parameter("rear_scan_topic", default_rear).value
        self.camera_topic = self.declare_parameter("camera_topic", default_camera).value
        self.front_yaw = float(self.declare_parameter("front_yaw", 0.0).value)
        self.rear_yaw = float(self.declare_parameter("rear_yaw", math.pi).value)
        self.danger_distance_m = float(self.declare_parameter("danger_distance_m", 0.35).value)
        self.caution_distance_m = float(self.declare_parameter("caution_distance_m", 0.80).value)
        self.enable_beep = bool(self.declare_parameter("enable_beep", False).value)

        self.latest_scans: Dict[str, LaserScan] = {}
        self.latest_camera: Optional[Image] = None
        self.last_beep_time = self.get_clock().now()
        self.beep_is_on = False
        self.sim_phase = 0.0

        self.merged_scan_pub = self.create_publisher(LaserScan, "/teacher/scan_merged", 10)
        self.state_pub = self.create_publisher(String, "/teacher/fusion_state", 10)
        self.rgb_pub = self.create_publisher(ColorRGBA, "/rgb", 10)
        self.beep_pub = self.create_publisher(UInt16, "/beep", 10)

        self.create_subscription(LaserScan, self.front_scan_topic, lambda msg: self.store_scan("front", msg), 10)
        self.create_subscription(LaserScan, self.rear_scan_topic, lambda msg: self.store_scan("rear", msg), 10)
        self.create_subscription(Image, self.camera_topic, self.store_camera, 10)

        if self.simulate:
            self.sim_front_pub = self.create_publisher(LaserScan, self.front_scan_topic, 10)
            self.sim_rear_pub = self.create_publisher(LaserScan, self.rear_scan_topic, 10)
            self.sim_camera_pub = self.create_publisher(Image, self.camera_topic, 10)
            self.create_timer(0.12, self.publish_simulated_sensors)

        self.create_timer(0.20, self.fuse_and_react)
        self.get_logger().info("Sensor fusion demo started")
        self.get_logger().info(
            f"front={self.front_scan_topic} rear={self.rear_scan_topic} "
            f"camera={self.camera_topic} simulate={self.simulate}"
        )

    def store_scan(self, name: str, msg: LaserScan) -> None:
        self.latest_scans[name] = msg

    def store_camera(self, msg: Image) -> None:
        self.latest_camera = msg

    def publish_simulated_sensors(self) -> None:
        self.sim_phase += 0.12
        front_obstacle = 0.25 + 0.75 * (0.5 + 0.5 * math.sin(self.sim_phase * 0.7))
        rear_obstacle = 0.40 + 0.95 * (0.5 + 0.5 * math.cos(self.sim_phase * 0.5))
        self.sim_front_pub.publish(self.make_fake_scan("scan0_frame", front_obstacle, math.sin(self.sim_phase) * 0.45))
        self.sim_rear_pub.publish(self.make_fake_scan("scan1_frame", rear_obstacle, math.cos(self.sim_phase) * 0.45))
        self.sim_camera_pub.publish(self.make_fake_image())

    def make_fake_scan(self, frame_id: str, obstacle_distance: float, obstacle_angle: float) -> LaserScan:
        msg = LaserScan()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = frame_id
        msg.angle_min = -math.pi / 2.0
        msg.angle_max = math.pi / 2.0
        msg.angle_increment = math.radians(1.0)
        msg.time_increment = 0.0
        msg.scan_time = 0.12
        msg.range_min = 0.08
        msg.range_max = 3.5
        count = int(round((msg.angle_max - msg.angle_min) / msg.angle_increment)) + 1
        ranges: List[float] = [2.8 for _ in range(count)]
        center = int(round((obstacle_angle - msg.angle_min) / msg.angle_increment))
        for offset in range(-4, 5):
            index = center + offset
            if 0 <= index < count:
                ranges[index] = obstacle_distance + abs(offset) * 0.025
        msg.ranges = ranges
        return msg

    def make_fake_image(self) -> Image:
        width = 40
        height = 30
        red = int(60 + 120 * (0.5 + 0.5 * math.sin(self.sim_phase * 0.8)))
        green = int(80 + 130 * (0.5 + 0.5 * math.sin(self.sim_phase * 0.6 + 1.0)))
        blue = int(50 + 150 * (0.5 + 0.5 * math.cos(self.sim_phase * 0.5)))

        msg = Image()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = "camera_color_optical_frame"
        msg.height = height
        msg.width = width
        msg.encoding = "rgb8"
        msg.is_bigendian = 0
        msg.step = width * 3
        msg.data = bytes([red, green, blue]) * (width * height)
        return msg

    def fuse_and_react(self) -> None:
        self.stop_beep_if_needed()

        scan_sources: List[Tuple[str, LaserScan, float]] = []
        if "front" in self.latest_scans:
            scan_sources.append(("front", self.latest_scans["front"], self.front_yaw))
        if "rear" in self.latest_scans:
            scan_sources.append(("rear", self.latest_scans["rear"], self.rear_yaw))

        if not scan_sources:
            self.publish_state("waiting for lidar scans")
            self.publish_rgb(0.0, 120.0, 255.0, 100.0)
            return

        merged, nearest = self.merge_scans(scan_sources)
        self.merged_scan_pub.publish(merged)

        camera_summary = self.analyze_camera(self.latest_camera)
        color, reason = self.choose_reaction(nearest, camera_summary)
        self.publish_rgb(*color)

        if self.enable_beep and nearest is not None and nearest < self.danger_distance_m:
            self.pulse_beep()

        nearest_text = "none" if nearest is None else f"{nearest:.2f}m"
        self.publish_state(f"nearest={nearest_text}; camera={camera_summary}; rgb={reason}")

    def merge_scans(self, scan_sources: List[Tuple[str, LaserScan, float]]) -> Tuple[LaserScan, Optional[float]]:
        angle_min = -math.pi
        angle_max = math.pi
        angle_increment = math.radians(1.0)
        count = int(round((angle_max - angle_min) / angle_increment)) + 1
        merged_ranges: List[float] = [float("inf") for _ in range(count)]
        nearest: Optional[float] = None

        # Use the latest input scan timestamp so it matches the odometry TF
        # (the microcontroller clock may differ from the system clock)
        latest_stamp = scan_sources[0][1].header.stamp
        for _name, scan, yaw_offset in scan_sources:
            if (scan.header.stamp.sec, scan.header.stamp.nanosec) > (latest_stamp.sec, latest_stamp.nanosec):
                latest_stamp = scan.header.stamp
            for angle, distance in finite_ranges(scan):
                merged_angle = math.atan2(math.sin(angle + yaw_offset), math.cos(angle + yaw_offset))
                index = int(round((merged_angle - angle_min) / angle_increment))
                if 0 <= index < count and distance < merged_ranges[index]:
                    merged_ranges[index] = distance
                if nearest is None or distance < nearest:
                    nearest = distance

        msg = LaserScan()
        msg.header.stamp = latest_stamp
        msg.header.frame_id = self.base_frame
        msg.angle_min = angle_min
        msg.angle_max = angle_max
        msg.angle_increment = angle_increment
        msg.time_increment = 0.0
        msg.scan_time = 0.2
        msg.range_min = 0.08
        msg.range_max = 3.5
        msg.ranges = [r if math.isfinite(r) else msg.range_max for r in merged_ranges]
        return msg, nearest

    def analyze_camera(self, msg: Optional[Image]) -> str:
        if msg is None or not msg.data:
            return "no camera"

        encoding = msg.encoding.lower()
        channels = 3
        order = "rgb"
        if encoding in ("mono8", "8uc1"):
            channels = 1
        elif encoding in ("rgba8", "bgra8"):
            channels = 4
            order = "rgb" if encoding == "rgba8" else "bgr"
        elif encoding == "bgr8":
            order = "bgr"
        elif encoding != "rgb8":
            return f"camera encoding {msg.encoding}"

        data = msg.data
        sample_count = 0
        red_total = 0
        green_total = 0
        blue_total = 0
        stride = max(channels, int(len(data) / 600) * channels)

        for index in range(0, len(data) - channels + 1, stride):
            if channels == 1:
                value = data[index]
                red = green = blue = value
            else:
                first = data[index]
                second = data[index + 1]
                third = data[index + 2]
                if order == "rgb":
                    red, green, blue = first, second, third
                else:
                    blue, green, red = first, second, third
            red_total += red
            green_total += green
            blue_total += blue
            sample_count += 1

        if sample_count == 0:
            return "camera empty"

        red_avg = red_total / sample_count
        green_avg = green_total / sample_count
        blue_avg = blue_total / sample_count
        brightness = (red_avg + green_avg + blue_avg) / 3.0

        if brightness < 45:
            return "dark"
        if red_avg > green_avg * 1.25 and red_avg > blue_avg * 1.25:
            return "red dominant"
        if green_avg > red_avg * 1.20 and green_avg > blue_avg * 1.20:
            return "green dominant"
        if blue_avg > red_avg * 1.20 and blue_avg > green_avg * 1.20:
            return "blue dominant"
        if brightness > 170:
            return "bright"
        return "balanced"

    def choose_reaction(self, nearest: Optional[float], camera_summary: str) -> Tuple[Tuple[float, float, float, float], str]:
        if nearest is not None and nearest < self.danger_distance_m:
            return (255.0, 0.0, 0.0, 100.0), "lidar danger"
        if nearest is not None and nearest < self.caution_distance_m:
            return (255.0, 210.0, 0.0, 100.0), "lidar caution"
        if camera_summary == "red dominant":
            return (255.0, 0.0, 0.0, 100.0), "camera red"
        if camera_summary == "green dominant":
            return (0.0, 255.0, 0.0, 100.0), "camera green"
        if camera_summary == "blue dominant":
            return (0.0, 90.0, 255.0, 100.0), "camera blue"
        if camera_summary == "bright":
            return (255.0, 255.0, 255.0, 100.0), "camera bright"
        if camera_summary == "dark":
            return (0.0, 150.0, 255.0, 100.0), "camera dark"
        return (0.0, 255.0, 90.0, 100.0), "clear"

    def publish_rgb(self, r: float, g: float, b: float, a: float) -> None:
        msg = ColorRGBA()
        msg.r = float(clamp(r, 0.0, 255.0))
        msg.g = float(clamp(g, 0.0, 255.0))
        msg.b = float(clamp(b, 0.0, 255.0))
        msg.a = float(a)
        self.rgb_pub.publish(msg)

    def publish_state(self, text: str) -> None:
        msg = String()
        msg.data = text
        self.state_pub.publish(msg)

    def pulse_beep(self) -> None:
        now = self.get_clock().now()
        if (now - self.last_beep_time).nanoseconds < 1_000_000_000:
            return
        msg = UInt16()
        msg.data = 1
        self.beep_pub.publish(msg)
        self.beep_is_on = True
        self.last_beep_time = now

    def stop_beep_if_needed(self) -> None:
        if not self.beep_is_on:
            return
        if (self.get_clock().now() - self.last_beep_time).nanoseconds < 100_000_000:
            return
        msg = UInt16()
        msg.data = 0
        self.beep_pub.publish(msg)
        self.beep_is_on = False


def main() -> None:
    rclpy.init()
    node = SensorFusionRgbDemo()
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
