from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    api_base = LaunchConfiguration("api_base")
    robot_id = LaunchConfiguration("robot_id")
    dry_run = LaunchConfiguration("dry_run")
    camera_topic = LaunchConfiguration("camera_topic")
    qr_topic = LaunchConfiguration("qr_topic")
    simulated_qr = LaunchConfiguration("simulated_qr")
    pickup_x = LaunchConfiguration("pickup_x")
    pickup_y = LaunchConfiguration("pickup_y")
    pickup_theta = LaunchConfiguration("pickup_theta")
    dropoff_x = LaunchConfiguration("dropoff_x")
    dropoff_y = LaunchConfiguration("dropoff_y")
    dropoff_theta = LaunchConfiguration("dropoff_theta")

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
            "dry_run",
            default_value="true",
            description="true = simulation sans mouvement robot"
        ),
        DeclareLaunchArgument(
            "camera_topic",
            default_value="/camera/color/image_raw/compressed",
            description="Topic camera pour lecture QR code"
        ),
        DeclareLaunchArgument("qr_topic", default_value="/qr_code"),
        DeclareLaunchArgument("simulated_qr", default_value="a"),
        DeclareLaunchArgument("pickup_x", default_value="2.62"),
        DeclareLaunchArgument("pickup_y", default_value="6.12"),
        DeclareLaunchArgument("pickup_theta", default_value="-1.90"),
        DeclareLaunchArgument("dropoff_x", default_value="1.32"),
        DeclareLaunchArgument("dropoff_y", default_value="2.18"),
        DeclareLaunchArgument("dropoff_theta", default_value="-1.90"),
        Node(
            package="m3pro_teacher_vision",
            executable="qr_code_reader_node",
            name="qr_code_reader_node",
            output="screen",
            parameters=[{
                "camera_topic": camera_topic,
                "qr_topic": qr_topic,
            }]
        ),
        Node(
            package="m3pro_teacher_vision",
            executable="mission_executor_node",
            name="mission_executor_node",
            output="screen",
            parameters=[{
                "api_base": api_base,
                "robot_id": robot_id,
                "dry_run": dry_run,
                "simulated_qr": simulated_qr,
                "pickup_x": pickup_x,
                "pickup_y": pickup_y,
                "pickup_theta": pickup_theta,
                "dropoff_x": dropoff_x,
                "dropoff_y": dropoff_y,
                "dropoff_theta": dropoff_theta,
            }]
        ),
    ])
