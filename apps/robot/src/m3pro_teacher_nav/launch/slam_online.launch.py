"""
Launch SLAM (slam_toolbox online async) for the M3 Pro.

Prerequisites: Yahboom bringup must already be running (lidar + odometry).
The bringup provides robot_state_publisher, EKF odometry, and lidar drivers.

This launch file starts:
  - sensor_fusion_rgb_demo (merged 360-degree scan)
  - slam_toolbox in online_async mode
  - rviz2 (optional)

NOTE: We do NOT launch our own robot_state_publisher here because the
Yahboom bringup already provides one. Running two would cause TF timestamp
conflicts (the microcontroller clock differs from the system clock).

Usage:
  ros2 launch m3pro_teacher_nav slam_online.launch.py
  ros2 launch m3pro_teacher_nav slam_online.launch.py rviz:=false
"""
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    nav_share = FindPackageShare("m3pro_teacher_nav")

    rviz_path = PathJoinSubstitution([nav_share, "rviz", "nav2_view.rviz"])
    slam_params = PathJoinSubstitution([nav_share, "config", "slam_toolbox_params.yaml"])

    return LaunchDescription([
        DeclareLaunchArgument("rviz", default_value="true"),
        DeclareLaunchArgument("use_sim_time", default_value="false"),

        # --- Yahboom odometry bridge (/odom_raw -> /odom + odom->base_link TF) ---
        Node(
            package="m3pro_teacher_demos",
            executable="odom_raw_bridge",
            parameters=[{
                "input_topic": "/odom_raw",
                "output_topic": "/odom",
                "odom_frame": "odom",
                "base_frame": "base_link",
                "publish_tf": True,
            }],
            output="screen",
        ),

        # --- Sensor fusion (merges front + rear lidar to 360-degree scan) ---
        Node(
            package="m3pro_teacher_demos",
            executable="sensor_fusion_rgb_demo",
            parameters=[{
                "simulate": False,
                "base_frame": "base_link",
                "front_scan_topic": "/scan0",
                "rear_scan_topic": "/scan1",
                "enable_beep": False,
            }],
            output="screen",
        ),

        # --- SLAM Toolbox ---
        Node(
            package="slam_toolbox",
            executable="async_slam_toolbox_node",
            name="slam_toolbox",
            parameters=[
                slam_params,
                {"use_sim_time": LaunchConfiguration("use_sim_time")},
            ],
            output="screen",
        ),

        # --- RViz ---
        Node(
            package="rviz2",
            executable="rviz2",
            arguments=["-d", rviz_path],
            condition=IfCondition(LaunchConfiguration("rviz")),
            output="screen",
        ),
    ])
