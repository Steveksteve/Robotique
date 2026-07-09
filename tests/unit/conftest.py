from __future__ import annotations

import sys
import types
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ROBOT_VISION = ROOT / "apps" / "robot" / "src" / "m3pro_teacher_vision"
ROBOT_DEMOS = ROOT / "apps" / "robot" / "src" / "m3pro_teacher_demos"

for path in (ROBOT_VISION, ROBOT_DEMOS):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))


def _module(name: str) -> types.ModuleType:
    module = types.ModuleType(name)
    sys.modules[name] = module
    return module


def _ensure_namespace(name: str) -> types.ModuleType:
    module = sys.modules.get(name)
    if module is None:
        module = _module(name)
    return module


class _FakeLogger:
    def info(self, *args, **kwargs):
        return None

    def warning(self, *args, **kwargs):
        return None

    def error(self, *args, **kwargs):
        return None

    def debug(self, *args, **kwargs):
        return None


class _FakeNode:
    def __init__(self, *args, **kwargs):
        self._logger = _FakeLogger()

    def declare_parameter(self, name, value):
        return types.SimpleNamespace(value=value)

    def create_publisher(self, *args, **kwargs):
        return types.SimpleNamespace(published=[], publish=lambda msg: None)

    def create_service(self, *args, **kwargs):
        return types.SimpleNamespace()

    def create_subscription(self, *args, **kwargs):
        return types.SimpleNamespace()

    def create_client(self, *args, **kwargs):
        return types.SimpleNamespace(
            wait_for_service=lambda timeout_sec=None: True,
            call_async=lambda request: None,
        )

    def create_timer(self, *args, **kwargs):
        return types.SimpleNamespace()

    def get_clock(self):
        return types.SimpleNamespace(now=lambda: types.SimpleNamespace(to_msg=lambda: None))

    def get_logger(self):
        return self._logger

    def destroy_node(self):
        return None


def _install_ros_stubs() -> None:
    rclpy = _module("rclpy")
    rclpy.init = lambda: None
    rclpy.spin = lambda node: None
    rclpy.shutdown = lambda: None
    rclpy.ok = lambda: False

    rclpy_node = _module("rclpy.node")
    rclpy_node.Node = _FakeNode
    rclpy.node = rclpy_node

    rclpy_action = _module("rclpy.action")
    rclpy_action.ActionClient = type("ActionClient", (), {})
    rclpy.action = rclpy_action

    rclpy_time = _module("rclpy.time")
    rclpy_time.Time = type("Time", (), {})
    rclpy.time = rclpy_time

    rclpy_duration = _module("rclpy.duration")
    rclpy_duration.Duration = type("Duration", (), {})
    rclpy.duration = rclpy_duration

    geometry_msgs = _ensure_namespace("geometry_msgs")
    geometry_msgs_msg = _module("geometry_msgs.msg")
    geometry_msgs_msg.PoseStamped = type("PoseStamped", (), {})
    geometry_msgs_msg.PoseArray = type("PoseArray", (), {})
    geometry_msgs_msg.Twist = type("Twist", (), {})
    geometry_msgs.msg = geometry_msgs_msg

    sensor_msgs = _ensure_namespace("sensor_msgs")
    sensor_msgs_msg = _module("sensor_msgs.msg")
    sensor_msgs_msg.CompressedImage = type("CompressedImage", (), {})
    sensor_msgs_msg.JointState = type("JointState", (), {})
    sensor_msgs.msg = sensor_msgs_msg

    std_msgs = _ensure_namespace("std_msgs")
    std_msgs_msg = _module("std_msgs.msg")
    std_msgs_msg.String = type("String", (), {"__init__": lambda self: setattr(self, "data", "")})
    std_msgs_msg.Header = type("Header", (), {})
    std_msgs.msg = std_msgs_msg

    std_srvs = _ensure_namespace("std_srvs")
    std_srvs_srv = _module("std_srvs.srv")
    std_srvs_srv.Trigger = type(
        "Trigger",
        (),
        {
            "Request": type("Request", (), {}),
            "Response": type("Response", (), {"__init__": lambda self: setattr(self, "success", False)}),
        },
    )
    std_srvs.srv = std_srvs_srv

    nav2_msgs = _ensure_namespace("nav2_msgs")
    nav2_msgs_action = _module("nav2_msgs.action")
    nav2_msgs_action.NavigateToPose = type("NavigateToPose", (), {"Goal": type("Goal", (), {})})
    nav2_msgs.action = nav2_msgs_action

    m3pro_teacher_interfaces = _ensure_namespace("m3pro_teacher_interfaces")
    m3pro_teacher_interfaces_srv = _module("m3pro_teacher_interfaces.srv")
    m3pro_teacher_interfaces_srv.Home = type("Home", (), {"Request": type("Request", (), {})})
    m3pro_teacher_interfaces_srv.SetJoints = type("SetJoints", (), {"Request": type("Request", (), {})})
    m3pro_teacher_interfaces.srv = m3pro_teacher_interfaces_srv

    tf2_ros = _module("tf2_ros")
    tf2_ros.Buffer = type("Buffer", (), {})
    tf2_ros.TransformListener = type("TransformListener", (), {})
    tf2_ros.TransformException = type("TransformException", (Exception,), {})

    arm_msgs = _ensure_namespace("arm_msgs")
    arm_msgs_msg = _module("arm_msgs.msg")
    arm_msgs_msg.ArmJoints = type("ArmJoints", (), {})
    arm_msgs.msg = arm_msgs_msg


def _install_image_stubs() -> None:
    numpy = _module("numpy")
    numpy.uint8 = object()
    numpy.frombuffer = lambda data, dtype: data

    cv2 = _module("cv2")
    cv2.IMREAD_COLOR = 1
    cv2.COLOR_BGR2GRAY = 2
    cv2.imdecode = lambda arr, flag: arr
    cv2.cvtColor = lambda frame, code: frame

    pyzbar = _ensure_namespace("pyzbar")
    pyzbar_pyzbar = _module("pyzbar.pyzbar")
    pyzbar_pyzbar.decode = lambda frame: []
    pyzbar.pyzbar = pyzbar_pyzbar


_install_ros_stubs()
_install_image_stubs()
