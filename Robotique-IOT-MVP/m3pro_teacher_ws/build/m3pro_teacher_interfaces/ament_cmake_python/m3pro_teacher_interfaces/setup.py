from setuptools import find_packages
from setuptools import setup

setup(
    name='m3pro_teacher_interfaces',
    version='0.1.0',
    packages=find_packages(
        include=('m3pro_teacher_interfaces', 'm3pro_teacher_interfaces.*')),
)
