from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import Command, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    description_share = FindPackageShare("m3pro_teacher_description")
    urdf_path = PathJoinSubstitution(
        [description_share, "urdf", "m3pro_teacher.urdf.xacro"]
    )
    rviz_path = PathJoinSubstitution(
        [description_share, "rviz", "m3pro_teacher.rviz"]
    )
    robot_description = ParameterValue(Command(["xacro ", urdf_path]), value_type=str)

    return LaunchDescription(
        [
            DeclareLaunchArgument("rviz", default_value="true"),
            DeclareLaunchArgument("camera_topic", default_value="/camera/color/image_raw"),
            DeclareLaunchArgument("danger_distance_m", default_value="0.35"),
            DeclareLaunchArgument("caution_distance_m", default_value="0.80"),
            DeclareLaunchArgument("enable_beep", default_value="false"),
            Node(
                package="robot_state_publisher",
                executable="robot_state_publisher",
                name="robot_state_publisher",
                parameters=[{"robot_description": robot_description}],
                remappings=[("/joint_states", "/teacher/joint_states")],
                output="screen",
            ),
            Node(
                package="m3pro_teacher_demos",
                executable="arm_joint_state_bridge_demo",
                name="arm_joint_state_bridge_demo",
                parameters=[
                    {
                        "demo_motion": False,
                        "joint_states_topic": "/teacher/joint_states",
                    }
                ],
                output="screen",
            ),
            Node(
                package="m3pro_teacher_demos",
                executable="sensor_fusion_rgb_demo",
                name="sensor_fusion_rgb_demo",
                parameters=[
                    {
                        "simulate": False,
                        "front_scan_topic": "/scan0",
                        "rear_scan_topic": "/scan1",
                        "camera_topic": LaunchConfiguration("camera_topic"),
                        "danger_distance_m": ParameterValue(
                            LaunchConfiguration("danger_distance_m"),
                            value_type=float,
                        ),
                        "caution_distance_m": ParameterValue(
                            LaunchConfiguration("caution_distance_m"),
                            value_type=float,
                        ),
                        "enable_beep": ParameterValue(
                            LaunchConfiguration("enable_beep"),
                            value_type=bool,
                        ),
                    }
                ],
                output="screen",
            ),
            Node(
                package="rviz2",
                executable="rviz2",
                name="rviz2",
                arguments=["-d", rviz_path],
                condition=IfCondition(LaunchConfiguration("rviz")),
                output="screen",
            ),
        ]
    )
