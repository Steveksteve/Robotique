from glob import glob
import os

from setuptools import setup

package_name = "m3pro_teacher_vision"

setup(
    name=package_name,
    version="0.1.0",
    packages=[package_name],
    data_files=[
        ("share/ament_index/resource_index/packages", [f"resource/{package_name}"]),
        (f"share/{package_name}", ["package.xml"]),
        (os.path.join("share", package_name, "launch"), glob("launch/*.launch.py")),
        (os.path.join("share", package_name, "config"), glob("config/*.yaml")),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="Teacher",
    maintainer_email="teacher@example.com",
    description="Object detection and pick-and-place for Yahboom M3 Pro.",
    license="MIT",
    entry_points={
        "console_scripts": [
            "object_detector_node = m3pro_teacher_vision.object_detector_node:main",
            "pick_and_place_node = m3pro_teacher_vision.pick_and_place_node:main",
            "camera_obstacle_node = m3pro_teacher_vision.camera_obstacle_node:main",
        ],
    },
)
