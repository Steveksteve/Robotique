cmake_minimum_required(VERSION 3.8)
project(m3pro_teacher_demos)

find_package(ament_cmake_python REQUIRED)
find_package(ament_cmake REQUIRED)

# Install Python modules
ament_python_install_package(${PROJECT_NAME})

# Install launch files
install(DIRECTORY
  launch
  DESTINATION share/${PROJECT_NAME}/
)

# Install scripts
install(DIRECTORY
  scripts
  DESTINATION share/${PROJECT_NAME}/
  USE_SOURCE_PERMISSIONS
)

ament_package()
