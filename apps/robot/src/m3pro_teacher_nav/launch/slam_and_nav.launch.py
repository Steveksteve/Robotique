"""
Launch SLAM + Nav2 simultaneously for explore-while-navigating.

The robot builds the map with slam_toolbox while Nav2 handles
obstacle avoidance and goal navigation. Perfect for autonomous exploration.

Prerequisites: Yahboom bringup must already be running.

NOTE: We rely on the Yahboom bringup's robot_state_publisher for TF.
Do not launch a second one — the microcontroller clock offset causes conflicts.

Usage:
  ros2 launch m3pro_teacher_nav slam_and_nav.launch.py
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
    nav2_params = PathJoinSubstitution([nav_share, "config", "nav2_params.yaml"])

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

        # --- Sensor fusion ---
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

        # --- SLAM Toolbox (provides map + map->odom TF) ---
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

        # --- Nav2 controller + planner (no AMCL needed, SLAM provides localization) ---
        Node(
            package="nav2_controller",
            executable="controller_server",
            name="controller_server",
            parameters=[nav2_params],
            remappings=[("cmd_vel", "/cmd_vel")],
            output="screen",
        ),
        Node(
            package="nav2_smoother",
            executable="smoother_server",
            name="smoother_server",
            parameters=[nav2_params],
            output="screen",
        ),
        Node(
            package="nav2_planner",
            executable="planner_server",
            name="planner_server",
            parameters=[nav2_params],
            output="screen",
        ),
        Node(
            package="nav2_behaviors",
            executable="behavior_server",
            name="behavior_server",
            parameters=[nav2_params],
            output="screen",
        ),
        Node(
            package="nav2_bt_navigator",
            executable="bt_navigator",
            name="bt_navigator",
            parameters=[nav2_params],
            output="screen",
        ),
        Node(
            package="nav2_lifecycle_manager",
            executable="lifecycle_manager",
            name="lifecycle_manager_navigation",
            parameters=[{
                "autostart": True,
                "node_names": [
                    "controller_server",
                    "smoother_server",
                    "planner_server",
                    "behavior_server",
                    "bt_navigator",
                ],
            }],
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
