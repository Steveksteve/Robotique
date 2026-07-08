#!/usr/bin/env python3
"""
Minimal ROS2 node that serves the web dashboard over HTTP.

It serves static files from the package's web/ directory and also provides
a /camera/snapshot endpoint that returns the latest camera frame as JPEG.
This avoids sending raw images through rosbridge (which is slow).

Usage:
  ros2 run m3pro_teacher_web web_server_node
  ros2 run m3pro_teacher_web web_server_node --ros-args -p port:=8080
"""
import io
import threading
from functools import partial
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image

try:
    import cv2
    import numpy as np
    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False


class CameraSnapshotHandler(SimpleHTTPRequestHandler):
    """HTTP handler that serves static files + a live camera JPEG endpoint."""

    def __init__(self, *args, jpeg_getter=None, **kwargs):
        self.jpeg_getter = jpeg_getter
        super().__init__(*args, **kwargs)

    def do_GET(self):
        if self.path == "/camera/snapshot":
            self.serve_snapshot()
        elif self.path == "/camera/stream":
            self.serve_mjpeg_stream()
        else:
            super().do_GET()

    def serve_snapshot(self):
        jpeg = self.jpeg_getter() if self.jpeg_getter else None
        if jpeg is None:
            self.send_error(503, "No camera frame available yet")
            return
        self.send_response(200)
        self.send_header("Content-Type", "image/jpeg")
        self.send_header("Content-Length", str(len(jpeg)))
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(jpeg)

    def serve_mjpeg_stream(self):
        self.send_response(200)
        self.send_header("Content-Type", "multipart/x-mixed-replace; boundary=frame")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        try:
            while True:
                jpeg = self.jpeg_getter() if self.jpeg_getter else None
                if jpeg is not None:
                    self.wfile.write(b"--frame\r\n")
                    self.wfile.write(b"Content-Type: image/jpeg\r\n")
                    self.wfile.write(f"Content-Length: {len(jpeg)}\r\n\r\n".encode())
                    self.wfile.write(jpeg)
                    self.wfile.write(b"\r\n")
                    self.wfile.flush()
                import time
                time.sleep(0.15)  # ~6 FPS to keep bandwidth low
        except (BrokenPipeError, ConnectionResetError):
            pass

    def log_message(self, format, *args):
        pass  # suppress per-request logs


class WebServerNode(Node):
    def __init__(self):
        super().__init__("web_server_node")
        self.port = int(self.declare_parameter("port", 8080).value)
        self.camera_topic = self.declare_parameter(
            "camera_topic", "/camera/color/image_raw"
        ).value

        self.latest_jpeg = None
        self.jpeg_lock = threading.Lock()

        if HAS_CV2:
            self.create_subscription(Image, self.camera_topic, self.on_image, 1)
            self.get_logger().info(f"Subscribed to camera: {self.camera_topic}")
        else:
            self.get_logger().warning(
                "OpenCV not found -- camera snapshot endpoint disabled. "
                "Install with: pip3 install opencv-python"
            )

        # Resolve web directory (installed share path)
        from ament_index_python.packages import get_package_share_directory
        web_dir = str(Path(get_package_share_directory("m3pro_teacher_web")) / "web")

        handler = partial(CameraSnapshotHandler, jpeg_getter=self.get_jpeg, directory=web_dir)
        self.httpd = HTTPServer(("0.0.0.0", self.port), handler)
        self.http_thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        self.http_thread.start()
        self.get_logger().info(f"Web dashboard: http://0.0.0.0:{self.port}")

    def on_image(self, msg: Image):
        """Convert ROS Image to JPEG and cache it."""
        try:
            encoding = msg.encoding.lower()
            h, w = msg.height, msg.width
            data = bytes(msg.data)

            if encoding in ("rgb8",):
                arr = np.frombuffer(data, dtype=np.uint8).reshape(h, w, 3)
                arr = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
            elif encoding in ("bgr8",):
                arr = np.frombuffer(data, dtype=np.uint8).reshape(h, w, 3)
            elif encoding in ("mono8", "8uc1"):
                arr = np.frombuffer(data, dtype=np.uint8).reshape(h, w)
            elif encoding in ("rgba8",):
                arr = np.frombuffer(data, dtype=np.uint8).reshape(h, w, 4)
                arr = cv2.cvtColor(arr, cv2.COLOR_RGBA2BGR)
            elif encoding in ("bgra8",):
                arr = np.frombuffer(data, dtype=np.uint8).reshape(h, w, 4)
                arr = cv2.cvtColor(arr, cv2.COLOR_BGRA2BGR)
            else:
                return

            # Downscale for bandwidth (max 320px wide)
            if w > 320:
                scale = 320.0 / w
                arr = cv2.resize(arr, (320, int(h * scale)))

            _, jpeg_buf = cv2.imencode(".jpg", arr, [cv2.IMWRITE_JPEG_QUALITY, 60])
            with self.jpeg_lock:
                self.latest_jpeg = jpeg_buf.tobytes()
        except Exception:
            pass

    def get_jpeg(self):
        with self.jpeg_lock:
            return self.latest_jpeg


def main():
    rclpy.init()
    node = WebServerNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.httpd.shutdown()
        try:
            node.destroy_node()
        except KeyboardInterrupt:
            pass
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
