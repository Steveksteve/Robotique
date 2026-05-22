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
                        "demo_motion": True,
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
                        "simulate": True,
                        "enable_beep": False,
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
