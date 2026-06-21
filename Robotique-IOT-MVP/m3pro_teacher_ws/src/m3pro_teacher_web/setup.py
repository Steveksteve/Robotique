from glob import glob
import os

from setuptools import setup

package_name = "m3pro_teacher_web"

setup(
    name=package_name,
    version="0.1.0",
    packages=[package_name],
    data_files=[
        ("share/ament_index/resource_index/packages", [f"resource/{package_name}"]),
        (f"share/{package_name}", ["package.xml"]),
        (os.path.join("share", package_name, "launch"), glob("launch/*.launch.py")),
        (os.path.join("share", package_name, "web"), glob("web/*")),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="Teacher",
    maintainer_email="teacher@example.com",
    description="Web dashboard for Yahboom M3 Pro robot monitoring.",
    license="MIT",
    entry_points={
        "console_scripts": [
            "web_server_node = m3pro_teacher_web.web_server_node:main",
        ],
    },
)
