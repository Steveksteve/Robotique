cmake_minimum_required(VERSION 3.8)
project(m3pro_teacher_nav)

find_package(ament_cmake REQUIRED)

install(
  DIRECTORY config launch maps rviz
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
