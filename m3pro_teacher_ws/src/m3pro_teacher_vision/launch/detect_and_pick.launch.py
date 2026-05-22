"""
Launch object detection, camera obstacle detection, and pick-and-place.

Prerequisites:
  - Yahboom bringup running (camera + arm driver)
  - robot_state_publisher running (for TF)

Usage:
  ros2 launch m3pro_teacher_vision detect_and_pick.launch.py
  ros2 launch m3pro_teacher_vision detect_and_pick.launch.py pick:=false  # detection only
"""
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    vision_share = FindPackageShare("m3pro_teacher_vision")
    params_file = PathJoinSubstitution([vision_share, "config", "detection_params.yaml"])

    return LaunchDescription([
        DeclareLaunchArgument("pick", default_value="true",
                              description="Enable pick-and-place (set false for detection only)"),

        # --- Camera obstacle detector (virtual scan for Nav2 costmap) ---
        Node(
            package="m3pro_teacher_vision",
            executable="camera_obstacle_node",
            name="camera_obstacle_node",
            parameters=[params_file],
            output="screen",
        ),

        # --- Object detector (color-based, for specific pickup targets) ---
        Node(
            package="m3pro_teacher_vision",
            executable="object_detector_node",
            name="object_detector_node",
            parameters=[params_file],
            output="screen",
        ),

        # --- Pick-and-place controller ---
        Node(
            package="m3pro_teacher_vision",
            executable="pick_and_place_node",
            name="pick_and_place_node",
            parameters=[params_file],
            condition=IfCondition(LaunchConfiguration("pick")),
            output="screen",
        ),
    ])
