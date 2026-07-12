#!/usr/bin/env python3
"""
Manual Arm Control Node for Yahboom M3 Pro.

Provides ROS2 services to control each joint of the arm independently.
Joints are controlled in Yahboom servo convention: 0-180 degrees, 90 = center.

Services:
  /arm/set_joint1 ... /arm/set_joint5  : SetJoint service (0-180 degrees)
  /arm/set_gripper                     : SetJoint service (0-180 degrees)
  /arm/set_all_joints                  : SetJoints service (6 values)
  /arm/home                            : Home service
  /arm/gripper_open / gripper_close    : Trigger services

Usage example:
  ros2 service call /arm/set_joint1 m3pro_teacher_interfaces/srv/SetJoint "{value: 120.0}"
  ros2 service call /arm/set_all_joints m3pro_teacher_interfaces/srv/SetJoints "{values: [90.0, 120.0, 10.0, 20.0, 90.0, 60.0]}"
  ros2 service call /arm/home m3pro_teacher_interfaces/srv/Home
"""
import rclpy
from rclpy.node import Node
from std_srvs.srv import Trigger
from std_msgs.msg import Float64MultiArray

try:
    from arm_msgs.msg import ArmJoints
    HAS_ARM_MSGS = True
except ImportError:
    HAS_ARM_MSGS = False
    ArmJoints = None

# Import custom service types
try:
    from m3pro_teacher_interfaces.srv import SetJoint, SetJoints, Home
    HAS_CUSTOM_SERVICES = True
except ImportError:
    HAS_CUSTOM_SERVICES = False


def clamp(value: float, low: float, high: float) -> float:
    """Clamp a value between low and high."""
    return max(low, min(high, value))


class ArmManualControlNode(Node):
    """ROS2 Node for manual control of the Yahboom M3 Pro arm."""

    def __init__(self):
        super().__init__("arm_manual_control_node")
        
        # Configuration
        self.arm_control_topic = self.declare_parameter(
            "arm_control_topic", "/arm6_joints"
        ).value
        
        # Current joint positions (0-180 degrees, Yahboom convention)
        self.joint_positions = [90.0, 90.0, 90.0, 90.0, 90.0]
        self.gripper_position = 90.0
        
        # Home positions (degrees, Yahboom convention)
        self.home_positions = [
            float(self.declare_parameter("home_joint1", 90.0).value),
            float(self.declare_parameter("home_joint2", 120.0).value),
            float(self.declare_parameter("home_joint3", 10.0).value),
            float(self.declare_parameter("home_joint4", 20.0).value),
            float(self.declare_parameter("home_joint5", 90.0).value),
            float(self.declare_parameter("home_joint6", 60.0).value),  # gripper open
        ]
        
        # Gripper open/close positions
        self.gripper_open = float(self.declare_parameter("gripper_open", 30.0).value)
        self.gripper_close = float(self.declare_parameter("gripper_close", 75.0).value)
        
        # Create publisher
        if HAS_ARM_MSGS:
            self.arm_pub = self.create_publisher(ArmJoints, self.arm_control_topic, 10)
            self.get_logger().info(f"Publishing ArmJoints to {self.arm_control_topic}")
        else:
            self.get_logger().warning("arm_msgs not available; using Float64MultiArray")
            self.arm_pub = self.create_publisher(
                Float64MultiArray, self.arm_control_topic, 10
            )
        
        # Create services
        if HAS_CUSTOM_SERVICES:
            self.create_service(SetJoint, "/arm/set_joint1", self._set_joint1_cb)
            self.create_service(SetJoint, "/arm/set_joint2", self._set_joint2_cb)
            self.create_service(SetJoint, "/arm/set_joint3", self._set_joint3_cb)
            self.create_service(SetJoint, "/arm/set_joint4", self._set_joint4_cb)
            self.create_service(SetJoint, "/arm/set_joint5", self._set_joint5_cb)
            self.create_service(SetJoint, "/arm/set_gripper", self._set_gripper_cb)
            self.create_service(SetJoints, "/arm/set_all_joints", self._set_all_joints_cb)
            self.create_service(Home, "/arm/home", self._home_cb)
            self.create_service(Trigger, "/arm/gripper_open", self._gripper_open_cb)
            self.create_service(Trigger, "/arm/gripper_close", self._gripper_close_cb)
            self.get_logger().info("Custom service types loaded successfully")
        else:
            self.get_logger().warning("Custom service types not available yet (compile workspace first)")
        
        self._print_info()
    
    def _print_info(self):
        """Print information about available services."""
        self.get_logger().info("=" * 60)
        self.get_logger().info("Arm Manual Control Node - Ready")
        self.get_logger().info("=" * 60)
        self.get_logger().info("Joint Control Services:")
        self.get_logger().info("  /arm/set_joint1 ... /arm/set_joint5  : Control individual joints (0-180°)")
        self.get_logger().info("  /arm/set_gripper                    : Control gripper (0-180°)")
        self.get_logger().info("  /arm/set_all_joints                 : Set all 6 values at once")
        self.get_logger().info("")
        self.get_logger().info("Predefined Poses:")
        self.get_logger().info("  /arm/home                           : Move to home position")
        self.get_logger().info("  /arm/gripper_open / gripper_close   : Quick gripper control")
        self.get_logger().info("")
        self.get_logger().info("Command Examples:")
        self.get_logger().info('  ros2 service call /arm/set_joint1 m3pro_teacher_interfaces/srv/SetJoint "{value: 120.0}"')
        self.get_logger().info('  ros2 service call /arm/home m3pro_teacher_interfaces/srv/Home "{}"')
        self.get_logger().info("=" * 60)
    
    # Service callback implementations
    def _set_joint1_cb(self, request, response):
        return self._set_joint(0, request.value, response)
    
    def _set_joint2_cb(self, request, response):
        return self._set_joint(1, request.value, response)
    
    def _set_joint3_cb(self, request, response):
        return self._set_joint(2, request.value, response)
    
    def _set_joint4_cb(self, request, response):
        return self._set_joint(3, request.value, response)
    
    def _set_joint5_cb(self, request, response):
        return self._set_joint(4, request.value, response)
    
    def _set_gripper_cb(self, request, response):
        self.gripper_position = clamp(float(request.value), 0.0, 180.0)
        self._publish_arm_command()
        response.success = True
        response.message = f"Gripper set to {self.gripper_position:.1f}°"
        self.get_logger().info(response.message)
        return response
    
    def _set_joint(self, joint_idx: int, value: float, response):
        """Generic joint setter."""
        self.joint_positions[joint_idx] = clamp(float(value), 0.0, 180.0)
        self._publish_arm_command()
        response.success = True
        joint_names = ["J1 (base_yaw)", "J2 (shoulder)", "J3 (elbow)", 
                      "J4 (wrist_pitch)", "J5 (wrist_roll)"]
        response.message = f"{joint_names[joint_idx]} set to {self.joint_positions[joint_idx]:.1f}°"
        self.get_logger().info(response.message)
        return response
    
    def _set_all_joints_cb(self, request, response):
        """Set all 6 joints at once."""
        if len(request.values) != 6:
            response.success = False
            response.message = f"Expected 6 values, got {len(request.values)}"
            self.get_logger().error(response.message)
            return response
        
        self.joint_positions = [clamp(float(v), 0.0, 180.0) for v in request.values[:5]]
        self.gripper_position = clamp(float(request.values[5]), 0.0, 180.0)
        self._publish_arm_command()
        response.success = True
        values_str = ", ".join([f'{v:.1f}°' for v in request.values])
        response.message = f"All joints set: [{values_str}]"
        self.get_logger().info(response.message)
        return response
    
    def _home_cb(self, request, response):
        """Move arm to home position."""
        self.joint_positions = self.home_positions[:5]
        self.gripper_position = self.home_positions[5]
        self._publish_arm_command()
        response.success = True
        response.message = "Moving to home position"
        self.get_logger().info(response.message)
        return response
    
    def _gripper_open_cb(self, request, response):
        """Open gripper."""
        self.gripper_position = self.gripper_open
        self._publish_arm_command()
        response.success = True
        response.message = f"Gripper opened ({self.gripper_open:.1f}°)"
        self.get_logger().info(response.message)
        return response
    
    def _gripper_close_cb(self, request, response):
        """Close gripper."""
        self.gripper_position = self.gripper_close
        self._publish_arm_command()
        response.success = True
        response.message = f"Gripper closed ({self.gripper_close:.1f}°)"
        self.get_logger().info(response.message)
        return response
    
    def _publish_arm_command(self):
        """Publish arm command to the arm driver."""
        if HAS_ARM_MSGS:
            msg = ArmJoints()
            msg.joint1 = int(self.joint_positions[0])
            msg.joint2 = int(self.joint_positions[1])
            msg.joint3 = int(self.joint_positions[2])
            msg.joint4 = int(self.joint_positions[3])
            msg.joint5 = int(self.joint_positions[4])
            msg.joint6 = int(self.gripper_position)
        else:
            msg = Float64MultiArray()
            msg.data = self.joint_positions + [self.gripper_position]
        
        self.arm_pub.publish(msg)


def main():
    rclpy.init()
    node = ArmManualControlNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        rclpy.shutdown()


if __name__ == "__main__":
    main()
