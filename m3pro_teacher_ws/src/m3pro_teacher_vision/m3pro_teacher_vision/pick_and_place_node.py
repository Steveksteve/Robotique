#!/usr/bin/env python3
"""
Pick-and-place controller for the Yahboom M3 Pro arm.

Workflow:
  1. Subscribe to /teacher/detections (PoseArray from object_detector_node)
  2. Transform detected object position from camera frame to base_link frame
  3. If object is within arm reach, compute inverse kinematics
  4. Command the arm to pick up the object
  5. Command Nav2 to drive to a drop-off location (or just open gripper)

The arm is controlled by publishing ArmJoints messages to the Yahboom driver.
Yahboom servo convention: 0-180 degrees, 90 = center position.

State machine: IDLE -> APPROACH -> REACH -> GRASP -> LIFT -> DONE -> IDLE
"""
import math
import time
from enum import Enum, auto

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseArray, Twist
from sensor_msgs.msg import JointState
from std_msgs.msg import Header

try:
    from arm_msgs.msg import ArmJoints
    HAS_ARM_MSGS = True
except ImportError:
    HAS_ARM_MSGS = False


class State(Enum):
    IDLE = auto()
    APPROACH = auto()
    REACH = auto()
    GRASP = auto()
    LIFT = auto()
    DONE = auto()


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


def rad_to_servo(rad, center=90.0):
    """Convert radians (0 = center) to Yahboom servo degrees (90 = center)."""
    return clamp(math.degrees(rad) + center, 0.0, 180.0)


class PickAndPlaceNode(Node):
    def __init__(self):
        super().__init__("pick_and_place_node")

        # --- Arm geometry (from URDF) ---
        self.arm_base_x = float(self.declare_parameter("arm_base_x", 0.02).value)
        self.arm_base_z = float(self.declare_parameter("arm_base_z", 0.24).value)
        self.L1 = float(self.declare_parameter("upper_arm_length", 0.11).value)
        self.L2 = float(self.declare_parameter("forearm_length", 0.11).value)
        self.L3 = float(self.declare_parameter("wrist_length", 0.12).value)

        self.arm_topic = self.declare_parameter("arm_command_topic", "/arm_control").value
        self.approach_dist = float(self.declare_parameter("approach_distance", 0.30).value)
        self.gripper_open = int(self.declare_parameter("gripper_open_value", 30).value)
        self.gripper_close = int(self.declare_parameter("gripper_close_value", 75).value)

        # --- State ---
        self.state = State.IDLE
        self.target = None  # (x, y, z) in base_link frame
        self.state_start_time = time.time()

        # --- TF2 listener ---
        from tf2_ros import Buffer, TransformListener
        from tf2_ros import TransformException
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)
        self.TransformException = TransformException

        # --- Subscribers ---
        self.create_subscription(PoseArray, "/teacher/detections", self.on_detections, 5)

        # --- Publishers ---
        self.cmd_vel_pub = self.create_publisher(Twist, "/cmd_vel", 10)
        self.joint_pub = self.create_publisher(JointState, "/teacher/joint_states", 10)
        if HAS_ARM_MSGS:
            self.arm_pub = self.create_publisher(ArmJoints, self.arm_topic, 10)
            self.get_logger().info(f"Arm control via ArmJoints on {self.arm_topic}")
        else:
            self.arm_pub = None
            self.get_logger().warning(
                "arm_msgs not available. Arm commands will be logged but not sent. "
                "Install yahboomcar packages for real arm control."
            )

        # --- Control loop (5 Hz) ---
        self.create_timer(0.2, self.control_loop)

        self.get_logger().info("Pick-and-place controller ready (state: IDLE)")

    def on_detections(self, msg: PoseArray):
        """Process detections from the object detector."""
        if self.state != State.IDLE:
            return  # busy with current pick

        if not msg.poses:
            return

        # Pick the nearest object with valid depth
        best = None
        best_dist = float("inf")
        for pose in msg.poses:
            z = pose.position.z
            if z <= 0:
                continue
            dist = math.sqrt(
                pose.position.x ** 2 + pose.position.y ** 2 + pose.position.z ** 2
            )
            if dist < best_dist:
                best_dist = dist
                best = pose

        if best is None:
            return

        # Transform from camera_color_optical_frame to base_link
        try:
            tf = self.tf_buffer.lookup_transform(
                "base_link", msg.header.frame_id,
                rclpy.time.Time(), timeout=rclpy.duration.Duration(seconds=0.5)
            )
            # Manual transform (quaternion rotation + translation)
            t = tf.transform.translation
            q = tf.transform.rotation
            px, py, pz = best.position.x, best.position.y, best.position.z
            # Apply rotation
            rx, ry, rz = self.quat_rotate(q.x, q.y, q.z, q.w, px, py, pz)
            bx = rx + t.x
            by = ry + t.y
            bz = rz + t.z

            self.target = (bx, by, bz)
            self.state = State.APPROACH
            self.state_start_time = time.time()
            self.get_logger().info(
                f"Target acquired at base_link ({bx:.3f}, {by:.3f}, {bz:.3f}). Approaching..."
            )
        except self.TransformException as e:
            self.get_logger().warning(f"TF lookup failed: {e}", throttle_duration_sec=2.0)

    @staticmethod
    def quat_rotate(qx, qy, qz, qw, px, py, pz):
        """Rotate point (px,py,pz) by quaternion (qx,qy,qz,qw)."""
        # Standard quaternion rotation formula: v' = q * v * q_conjugate
        rx = px + 2.0 * (-(qy*qy + qz*qz)*px + (qx*qy - qw*qz)*py + (qx*qz + qw*qy)*pz)
        ry = py + 2.0 * ((qx*qy + qw*qz)*px - (qx*qx + qz*qz)*py + (qy*qz - qw*qx)*pz)
        rz = pz + 2.0 * ((qx*qz - qw*qy)*px + (qy*qz + qw*qx)*py - (qx*qx + qy*qy)*pz)
        return rx, ry, rz

    def control_loop(self):
        elapsed = time.time() - self.state_start_time

        if self.state == State.IDLE:
            return

        elif self.state == State.APPROACH:
            self.do_approach(elapsed)

        elif self.state == State.REACH:
            self.do_reach(elapsed)

        elif self.state == State.GRASP:
            self.do_grasp(elapsed)

        elif self.state == State.LIFT:
            self.do_lift(elapsed)

        elif self.state == State.DONE:
            self.get_logger().info("Pick complete! Returning to IDLE.")
            self.state = State.IDLE
            self.target = None

    def do_approach(self, elapsed):
        """Drive toward the object until within arm reach."""
        if self.target is None:
            self.state = State.IDLE
            return

        tx, ty, tz = self.target
        dist = math.sqrt(tx ** 2 + ty ** 2)
        angle = math.atan2(ty, tx)

        twist = Twist()

        if abs(angle) > 0.15:
            # Rotate toward object
            twist.angular.z = clamp(angle * 1.5, -0.5, 0.5)
        elif dist > self.approach_dist:
            # Drive forward
            twist.linear.x = clamp((dist - self.approach_dist) * 0.5, 0.0, 0.12)
            twist.angular.z = clamp(angle * 0.8, -0.3, 0.3)
        else:
            # Close enough -- stop and switch to REACH
            twist.linear.x = 0.0
            twist.angular.z = 0.0
            self.cmd_vel_pub.publish(twist)
            self.transition_to(State.REACH)
            return

        self.cmd_vel_pub.publish(twist)

        if elapsed > 30.0:
            self.get_logger().warning("Approach timeout, aborting")
            self.stop_and_reset()

    def do_reach(self, elapsed):
        """Move arm to pre-grasp position above the object."""
        if self.target is None:
            self.state = State.IDLE
            return

        tx, ty, tz = self.target

        # Compute IK and send arm to position above object
        joints = self.compute_ik(tx, ty, tz + 0.05)  # 5cm above
        if joints is None:
            self.get_logger().warning("Object out of arm reach, aborting")
            self.stop_and_reset()
            return

        self.send_arm_command(*joints, gripper=self.gripper_open)

        if elapsed > 2.0:
            # Lower to object
            joints_low = self.compute_ik(tx, ty, tz)
            if joints_low:
                self.send_arm_command(*joints_low, gripper=self.gripper_open)
            self.transition_to(State.GRASP)

    def do_grasp(self, elapsed):
        """Close gripper on object."""
        if self.target is None:
            self.state = State.IDLE
            return

        tx, ty, tz = self.target
        joints = self.compute_ik(tx, ty, tz)
        if joints:
            self.send_arm_command(*joints, gripper=self.gripper_close)

        if elapsed > 1.5:
            self.transition_to(State.LIFT)

    def do_lift(self, elapsed):
        """Lift the object up."""
        # Move to home-like raised position
        self.send_arm_command(
            base_yaw=0.0,
            shoulder=math.radians(30.0),
            elbow=math.radians(-60.0),
            wrist_pitch=math.radians(-30.0),
            wrist_roll=0.0,
            gripper=self.gripper_close,
        )

        if elapsed > 2.0:
            self.transition_to(State.DONE)
            # Open gripper to release
            self.send_arm_command(
                base_yaw=0.0,
                shoulder=math.radians(30.0),
                elbow=math.radians(-60.0),
                wrist_pitch=math.radians(-30.0),
                wrist_roll=0.0,
                gripper=self.gripper_open,
            )

    def compute_ik(self, tx, ty, tz):
        """
        Simple analytical IK for the M3 Pro arm.

        Given target (tx, ty, tz) in base_link frame, compute joint angles.
        The arm has: base_yaw (Z), shoulder (Y), elbow (Y), wrist_pitch (Y), wrist_roll (X).

        We use a 2-link planar IK for shoulder + elbow, then set wrist
        to point the gripper downward.

        Returns (base_yaw, shoulder, elbow, wrist_pitch, wrist_roll) in radians,
        or None if unreachable.
        """
        # Position relative to arm base
        dx = tx - self.arm_base_x
        dy = ty
        dz = tz - self.arm_base_z  # relative to shoulder height

        # Base yaw
        base_yaw = math.atan2(dy, dx)

        # Distance in the arm plane
        r = math.sqrt(dx ** 2 + dy ** 2)  # horizontal distance from arm base

        # We want the gripper to point downward, so the wrist endpoint is
        # (r, dz) and the gripper extends L3 downward from it.
        # Effective target for the 2-link IK:
        ik_r = r
        ik_z = dz + self.L3  # wrist joint needs to be L3 above the target

        # 2-link planar IK (shoulder + elbow)
        d = math.sqrt(ik_r ** 2 + ik_z ** 2)
        if d > self.L1 + self.L2 or d < abs(self.L1 - self.L2):
            return None  # unreachable

        # Law of cosines for elbow angle
        cos_elbow = (self.L1 ** 2 + self.L2 ** 2 - d ** 2) / (2 * self.L1 * self.L2)
        cos_elbow = clamp(cos_elbow, -1.0, 1.0)
        elbow = -(math.pi - math.acos(cos_elbow))  # negative = elbow bends down

        # Shoulder angle
        alpha = math.atan2(ik_z, ik_r)
        cos_beta = (self.L1 ** 2 + d ** 2 - self.L2 ** 2) / (2 * self.L1 * d)
        cos_beta = clamp(cos_beta, -1.0, 1.0)
        beta = math.acos(cos_beta)
        shoulder = alpha + beta

        # Wrist pitch: compensate so gripper points straight down
        wrist_pitch = -(shoulder + elbow) - math.pi / 2

        # Check joint limits (all +-1.57 rad)
        limit = 1.57
        for angle in [base_yaw, shoulder, elbow, wrist_pitch]:
            if abs(angle) > limit:
                return None

        return base_yaw, shoulder, elbow, wrist_pitch, 0.0

    def send_arm_command(self, base_yaw, shoulder, elbow, wrist_pitch, wrist_roll, gripper):
        """Send arm joint command via ArmJoints message."""
        j1 = int(rad_to_servo(base_yaw))
        j2 = int(rad_to_servo(shoulder))
        j3 = int(rad_to_servo(elbow))
        j4 = int(rad_to_servo(wrist_pitch))
        j5 = int(rad_to_servo(wrist_roll))
        j6 = int(gripper)

        self.get_logger().debug(
            f"Arm cmd: j1={j1} j2={j2} j3={j3} j4={j4} j5={j5} j6={j6}"
        )

        if HAS_ARM_MSGS and self.arm_pub is not None:
            msg = ArmJoints()
            msg.joint1 = j1
            msg.joint2 = j2
            msg.joint3 = j3
            msg.joint4 = j4
            msg.joint5 = j5
            msg.joint6 = j6
            self.arm_pub.publish(msg)
        else:
            self.get_logger().info(
                f"[DRY RUN] Would send arm: [{j1},{j2},{j3},{j4},{j5},{j6}]",
                throttle_duration_sec=1.0,
            )

        # Also publish as JointState for visualization
        js = JointState()
        js.header.stamp = self.get_clock().now().to_msg()
        js.name = [
            "base_yaw_joint", "shoulder_joint", "elbow_joint",
            "wrist_pitch_joint", "wrist_roll_joint",
            "left_finger_joint", "right_finger_joint",
        ]
        gripper_m = clamp((90.0 - float(j6)) / 60.0 * 0.04, 0.0, 0.04)
        js.position = [base_yaw, shoulder, elbow, wrist_pitch, wrist_roll, gripper_m, gripper_m]
        self.joint_pub.publish(js)

    def transition_to(self, new_state):
        self.get_logger().info(f"State: {self.state.name} -> {new_state.name}")
        self.state = new_state
        self.state_start_time = time.time()

    def stop_and_reset(self):
        twist = Twist()
        self.cmd_vel_pub.publish(twist)
        # Return arm to home
        self.send_arm_command(0.0, math.radians(30), math.radians(-80),
                             math.radians(-70), 0.0, self.gripper_open)
        self.state = State.IDLE
        self.target = None


def main():
    rclpy.init()
    node = PickAndPlaceNode()
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
