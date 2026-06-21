# Connectez-vous au Jetson et lancez l'agent robot
ssh jetson@10.10.221.123
bash /home/jetson/start_agent.sh

# lancer le conteneur sur le robot
docker start infallible_kare
# build Docker sur le PC
cd /mnt/c/hetic/aaaa/m3pro_teacher_ws
docker build -t m3pro_teacher_ws:humble .

# Entrez ensuite dans le conteneur ROS2
docker exec -it infallible_kare bash

# build dans le conteneur
cd /root/m3pro_teacher_ws
source /opt/ros/humble/setup.bash
colcon build --symlink-install
source install/setup.bash
ros2 pkg list | grep m3pro_teacher

# lancer le slam rviz dans le conteneur

ros2 launch m3pro_teacher_nav slam_online.launch.py
