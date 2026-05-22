FROM ros:humble-ros-base

ENV DEBIAN_FRONTEND=noninteractive
SHELL ["/bin/bash", "-c"]

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-colcon-common-extensions \
    python3-opencv \
    ros-humble-joint-state-publisher-gui \
    ros-humble-navigation2 \
    ros-humble-nav2-bringup \
    ros-humble-robot-state-publisher \
    ros-humble-rosbridge-server \
    ros-humble-rviz2 \
    ros-humble-slam-toolbox \
    ros-humble-tf2-tools \
    ros-humble-xacro \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /root/m3pro_teacher_ws

COPY src ./src
COPY scripts ./scripts
COPY *.md ./

RUN source /opt/ros/humble/setup.bash \
  && colcon build --symlink-install

# Setup bashrc with ROS sources
RUN echo "source /opt/ros/humble/setup.bash" >> /root/.bashrc \
  && echo "source /root/m3pro_teacher_ws/install/setup.bash" >> /root/.bashrc
