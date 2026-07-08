from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument("api_base", default_value="http://localhost:8000"),
        DeclareLaunchArgument("robot_id", default_value="raa-robot-01"),
        DeclareLaunchArgument("dry_run", default_value="true"),
        DeclareLaunchArgument("camera_topic", default_value="/camera/color/image_raw"),

        Node(
            package="m3pro_teacher_vision",
            executable="qr_code_reader_node",
            name="qr_code_reader_node",
            parameters=[{
                "camera_topic": LaunchConfiguration("camera_topic"),
                "qr_topic": "/qr_code",
            }],
            output="screen",
        ),

        Node(
            package="m3pro_teacher_vision",
            executable="mission_executor_node",
            name="mission_executor_node",
            parameters=[{
                "api_base": LaunchConfiguration("api_base"),
                "robot_id": LaunchConfiguration("robot_id"),
                "dry_run": LaunchConfiguration("dry_run"),
                "pickup_x": 2.62,
                "pickup_y": 6.12,
                "pickup_theta": -1.90,
                "dropoff_x": 1.32,
                "dropoff_y": 2.18,
                "dropoff_theta": -1.90,
                "simulated_qr": "a",
            }],
            output="screen",
        ),
    ])
