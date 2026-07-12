#!/usr/bin/env python3
"""
Simple CLI tool to control the Yahboom M3 Pro arm via ROS2 services.

Usage:
  python3 arm_control_cli.py set_joint1 120.0
  python3 arm_control_cli.py set_gripper 60.0
  python3 arm_control_cli.py home
  python3 arm_control_cli.py set_all 90 120 10 20 90 60
"""
import sys
import time
import rclpy
from rclpy.node import Node
from std_srvs.srv import Trigger

# Import custom service types
try:
    from m3pro_teacher_interfaces.srv import SetJoint, SetJoints, Home
    HAS_SERVICES = True
except ImportError:
    HAS_SERVICES = False
    print("ERROR: Custom service types not found. Did you compile the workspace?")
    print("Run: colcon build --symlink-install")
    sys.exit(1)


class ArmControlClient(Node):
    def __init__(self):
        super().__init__("arm_control_cli")
        self.cli_joint = self.create_client(SetJoint, "/arm/set_joint1")
        self.cli_gripper = self.create_client(SetJoint, "/arm/set_gripper")
        self.cli_all_joints = self.create_client(SetJoints, "/arm/set_all_joints")
        self.cli_home = self.create_client(Home, "/arm/home")
        self.cli_gripper_open = self.create_client(Trigger, "/arm/gripper_open")
        self.cli_gripper_close = self.create_client(Trigger, "/arm/gripper_close")
    
    def wait_for_service(self, client, timeout=5.0):
        """Wait for a service to be available."""
        start = time.time()
        while not client.wait_for_service(timeout_sec=1.0):
            if time.time() - start > timeout:
                return False
        return True
    
    def set_joint(self, joint_num: int, value: float):
        """Set a single joint value."""
        clients = [
            self.create_client(SetJoint, f"/arm/set_joint{i+1}")
            for i in range(5)
        ]
        client = clients[joint_num - 1]
        
        if not self.wait_for_service(client):
            print(f"ERROR: Service /arm/set_joint{joint_num} not available")
            return False
        
        request = SetJoint.Request()
        request.value = float(value)
        future = client.call_async(request)
        rclpy.spin_until_future_complete(self, future)
        
        if future.result() is not None:
            response = future.result()
            print(f"[OK] {response.message}")
            return True
        else:
            print("ERROR: Service call failed")
            return False
    
    def set_gripper(self, value: float):
        """Set gripper position."""
        if not self.wait_for_service(self.cli_gripper):
            print("ERROR: Service /arm/set_gripper not available")
            return False
        
        request = SetJoint.Request()
        request.value = float(value)
        future = self.cli_gripper.call_async(request)
        rclpy.spin_until_future_complete(self, future)
        
        if future.result() is not None:
            print(f"[OK] {future.result().message}")
            return True
        else:
            print("ERROR: Service call failed")
            return False
    
    def set_all_joints(self, values):
        """Set all 6 joints at once."""
        if len(values) != 6:
            print(f"ERROR: Expected 6 values, got {len(values)}")
            return False
        
        if not self.wait_for_service(self.cli_all_joints):
            print("ERROR: Service /arm/set_all_joints not available")
            return False
        
        request = SetJoints.Request()
        request.values = [float(v) for v in values]
        future = self.cli_all_joints.call_async(request)
        rclpy.spin_until_future_complete(self, future)
        
        if future.result() is not None:
            print(f"[OK] {future.result().message}")
            return True
        else:
            print("ERROR: Service call failed")
            return False
    
    def home(self):
        """Move to home position."""
        if not self.wait_for_service(self.cli_home):
            print("ERROR: Service /arm/home not available")
            return False
        
        request = Home.Request()
        future = self.cli_home.call_async(request)
        rclpy.spin_until_future_complete(self, future)
        
        if future.result() is not None:
            print(f"[OK] {future.result().message}")
            return True
        else:
            print("ERROR: Service call failed")
            return False
    
    def gripper_open(self):
        """Open gripper."""
        if not self.wait_for_service(self.cli_gripper_open):
            print("ERROR: Service /arm/gripper_open not available")
            return False
        
        request = Trigger.Request()
        future = self.cli_gripper_open.call_async(request)
        rclpy.spin_until_future_complete(self, future)
        
        if future.result() is not None:
            print(f"[OK] {future.result().message}")
            return True
        else:
            print("ERROR: Service call failed")
            return False
    
    def gripper_close(self):
        """Close gripper."""
        if not self.wait_for_service(self.cli_gripper_close):
            print("ERROR: Service /arm/gripper_close not available")
            return False
        
        request = Trigger.Request()
        future = self.cli_gripper_close.call_async(request)
        rclpy.spin_until_future_complete(self, future)
        
        if future.result() is not None:
            print(f"[OK] {future.result().message}")
            return True
        else:
            print("ERROR: Service call failed")
            return False


def print_usage():
    print("""
ARM CONTROL CLI - Yahboom M3 Pro Manual Control

Usage:
  python3 arm_control_cli.py <command> [args...]

Commands:
  joint1 <angle>           Control base_yaw joint (0-180°)
  joint2 <angle>           Control shoulder joint (0-180°)
  joint3 <angle>           Control elbow joint (0-180°)
  joint4 <angle>           Control wrist_pitch joint (0-180°)
  joint5 <angle>           Control wrist_roll joint (0-180°)
  gripper <angle>          Control gripper (0-180°)
  all <j1> <j2> <j3> <j4> <j5> <gripper>  Set all 6 values
  home                     Move to home position
  open                     Open gripper
  close                    Close gripper

Examples:
  python3 arm_control_cli.py joint1 120.0
  python3 arm_control_cli.py gripper 30.0
  python3 arm_control_cli.py all 90 120 10 20 90 60
  python3 arm_control_cli.py home
  python3 arm_control_cli.py open
    """)


def main():
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)
    
    rclpy.init()
    client = ArmControlClient()
    
    cmd = sys.argv[1].lower()
    
    try:
        if cmd == "help":
            print_usage()
        elif cmd == "home":
            client.home()
        elif cmd == "open":
            client.gripper_open()
        elif cmd == "close":
            client.gripper_close()
        elif cmd.startswith("joint") and len(cmd) == 6 and cmd[5].isdigit():
            joint_num = int(cmd[5])
            if joint_num < 1 or joint_num > 5:
                print(f"ERROR: Joint number must be 1-5, got {joint_num}")
                sys.exit(1)
            if len(sys.argv) < 3:
                print(f"ERROR: Missing angle value for joint{joint_num}")
                sys.exit(1)
            client.set_joint(joint_num, sys.argv[2])
        elif cmd == "gripper":
            if len(sys.argv) < 3:
                print("ERROR: Missing angle value for gripper")
                sys.exit(1)
            client.set_gripper(sys.argv[2])
        elif cmd == "all":
            if len(sys.argv) < 8:
                print("ERROR: Expected 6 values for 'all' command")
                sys.exit(1)
            client.set_all_joints(sys.argv[2:8])
        else:
            print(f"ERROR: Unknown command '{cmd}'")
            print_usage()
            sys.exit(1)
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    finally:
        rclpy.shutdown()


if __name__ == "__main__":
    main()
