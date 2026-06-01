"""
Launch the web monitoring dashboard.

Starts:
  - rosbridge_websocket (WebSocket bridge on port 9090)
  - web_server_node (HTTP server on port 8080)
  - arm_manual_control_node (ROS services used by the Arm panel)

Then open http://<jetson-ip>:8080 in any browser.

Usage:
  ros2 launch m3pro_teacher_web web_dashboard.launch.py
  ros2 launch m3pro_teacher_web web_dashboard.launch.py port:=8080
"""
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    rosbridge_share = FindPackageShare("rosbridge_server")

    return LaunchDescription([
        DeclareLaunchArgument("port", default_value="8080"),
        DeclareLaunchArgument("camera_topic", default_value="/camera/color/image_raw"),
        DeclareLaunchArgument("rosbridge", default_value="true"),
        DeclareLaunchArgument("arm_control", default_value="true"),
        DeclareLaunchArgument("arm_control_topic", default_value="/arm6_joints"),

        # --- rosbridge WebSocket server (port 9090) ---
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                PathJoinSubstitution([rosbridge_share, "launch", "rosbridge_websocket_launch.xml"])
            ),
            condition=IfCondition(LaunchConfiguration("rosbridge")),
        ),

        # --- Arm service backend used by the existing dashboard Arm panel ---
        Node(
            package="m3pro_teacher_demos",
            executable="arm_manual_control_node",
            name="arm_manual_control_node",
            parameters=[{
                "arm_control_topic": LaunchConfiguration("arm_control_topic"),
            }],
            condition=IfCondition(LaunchConfiguration("arm_control")),
            output="screen",
        ),

        # --- Web file server + camera snapshot ---
        Node(
            package="m3pro_teacher_web",
            executable="web_server_node",
            name="web_server_node",
            parameters=[{
                "port": ParameterValue(LaunchConfiguration("port"), value_type=int),
                "camera_topic": LaunchConfiguration("camera_topic"),
            }],
            output="screen",
        ),
    ])
