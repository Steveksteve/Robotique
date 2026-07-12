from setuptools import setup
from glob import glob
import os

package_name = "m3pro_teacher_vision"

setup(
    name=package_name,
    version="0.0.1",
    packages=[package_name],
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        (os.path.join("share", package_name, "launch"), glob("launch/*.launch.py")),
        (os.path.join("share", package_name, "config"), glob("config/*.yaml")),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="RAA",
    maintainer_email="raa@example.com",
    description="Vision, QR code and mission executor for RAA MVP",
    license="MIT",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "qr_code_reader_node = m3pro_teacher_vision.qr_code_reader_node:main",
            "mission_executor_node = m3pro_teacher_vision.mission_executor_node:main",
            "object_detector_node = m3pro_teacher_vision.object_detector_node:main",
            "pick_and_place_node = m3pro_teacher_vision.pick_and_place_node:main",
            "camera_obstacle_node = m3pro_teacher_vision.camera_obstacle_node:main",
        ],
    },
)
