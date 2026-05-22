from glob import glob
import os

from setuptools import setup

package_name = "m3pro_teacher_demos"

setup(
    name=package_name,
    version="0.1.0",
    packages=[package_name],
    data_files=[
        ("share/ament_index/resource_index/packages", [f"resource/{package_name}"]),
        (f"share/{package_name}", ["package.xml"]),
        (os.path.join("share", package_name, "launch"), glob("launch/*.launch.py")),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="Teacher",
    maintainer_email="teacher@example.com",
    description="Teacher demo nodes for Yahboom M3 Pro ROS2.",
    license="MIT",
    entry_points={
        "console_scripts": [
            "tf2_sensor_frames_demo = m3pro_teacher_demos.tf2_sensor_frames_demo:main",
            "arm_joint_state_bridge_demo = m3pro_teacher_demos.arm_joint_state_bridge_demo:main",
            "odom_raw_bridge = m3pro_teacher_demos.odom_raw_bridge:main",
            "sensor_fusion_rgb_demo = m3pro_teacher_demos.sensor_fusion_rgb_demo:main",
            "frontier_explorer_demo = m3pro_teacher_demos.frontier_explorer_demo:main",
        ],
    },
)
