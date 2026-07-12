from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    api_base = LaunchConfiguration("api_base")
    robot_id = LaunchConfiguration("robot_id")
    ws_url = LaunchConfiguration("ws_url")
    dry_run = LaunchConfiguration("dry_run")
    simulated_qr = LaunchConfiguration("simulated_qr")
    camera_topic = LaunchConfiguration("camera_topic")
    poll_seconds = LaunchConfiguration("poll_seconds")

    return LaunchDescription([
        DeclareLaunchArgument(
            "api_base",
            default_value="http://localhost:8000",
            description="URL du back-end API missions"
        ),
        DeclareLaunchArgument(
            "robot_id",
            default_value="raa-robot-01",
            description="Identifiant logique du robot"
        ),
        DeclareLaunchArgument(
            "ws_url",
            default_value="",
            description="URL WebSocket temps réel, ex: ws://serveur:8765. Vide = désactivé."
        ),
        DeclareLaunchArgument(
            "dry_run",
            default_value="true",
            description="true = simulation sans mouvement robot"
        ),
        DeclareLaunchArgument(
            "simulated_qr",
            default_value="a",
            description="QR renvoyé en dry-run"
        ),
        DeclareLaunchArgument(
            "camera_topic",
            default_value="/camera/color/image_raw/compressed",
            description="Topic camera compressé pour lecture QR code"
        ),
        DeclareLaunchArgument(
            "poll_seconds",
            default_value="2.0",
            description="Période de polling API mission"
        ),
        Node(
            package="m3pro_teacher_vision",
            executable="qr_code_reader_node",
            name="qr_code_reader_node",
            output="screen",
            parameters=[{
                "camera_topic": camera_topic
            }]
        ),
        Node(
            package="m3pro_teacher_vision",
            executable="mission_executor_node",
            name="mission_executor_node",
            output="screen",
            parameters=[{
                "api_base": api_base,
                "ws_url": ws_url,
                "robot_id": robot_id,
                "dry_run": dry_run,
                "simulated_qr": simulated_qr,
                "poll_seconds": poll_seconds,
            }]
        ),
    ])
