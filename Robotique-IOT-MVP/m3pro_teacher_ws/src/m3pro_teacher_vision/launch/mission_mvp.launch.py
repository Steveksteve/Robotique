from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    api_base = LaunchConfiguration("api_base")
    dry_run = LaunchConfiguration("dry_run")
    camera_topic = LaunchConfiguration("camera_topic")

    return LaunchDescription([
        DeclareLaunchArgument(
            "api_base",
            default_value="http://localhost:8000",
            description="URL du back-end API missions"
        ),
        DeclareLaunchArgument(
            "dry_run",
            default_value="true",
            description="true = simulation sans mouvement robot"
        ),
        DeclareLaunchArgument(
            "camera_topic",
            default_value="/camera/color/image_raw",
            description="Topic camera pour lecture QR code"
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
                "dry_run": dry_run
            }]
        ),
    ])
