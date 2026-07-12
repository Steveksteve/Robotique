# RAA - État du pipeline robot final

## Ce qui fonctionne

- Docker PC OK
- API OK sur http://localhost:8000/health
- Web OK sur http://localhost:8080
- WebSocket OK sur ws://localhost:8765
- Fake robot OK
- Vrai robot connecté au serveur PC OK
- Workspace ROS 2 déployé sur le robot
- Build colcon OK
- Mission en dry_run validée jusqu'à COMPLETED depuis le dashboard

## Robot

Conteneur ROS 2 utilisé :

peaceful_ride

Robot testé :

Yahboom ROSMASTER M3 Pro Jetson Nano

## IP utilisées pendant les tests

PC serveur :

10.10.220.67

Robot :

10.10.220.79

Ces IP peuvent changer selon le réseau.

## Commande mission dry_run validée

Dans le conteneur robot :

source /opt/ros/humble/setup.bash
source /root/yahboomcar_ws/install/setup.bash 2>/dev/null || true
source /root/M3Pro_ws/install/setup.bash 2>/dev/null || true
source /root/m3pro_teacher_ws/install/setup.bash

ros2 launch m3pro_teacher_vision mission_mvp.launch.py \
  api_base:=http://10.10.220.67:8000 \
  ws_url:=ws://10.10.220.67:8765 \
  robot_id:=raa-robot-01 \
  dry_run:=true \
  simulated_qr:=a

Résultat :

Mission COMPLETED depuis le dashboard.

## Problème en cours : QR code / caméra

Le paquet pyzbar a été installé dans le conteneur :

apt update
apt install -y python3-pip libzbar0
python3 -m pip install pyzbar

Test pyzbar OK :

python3 - <<'PY'
from pyzbar.pyzbar import decode
print("pyzbar OK")
PY

Le node QR démarre avec :

ros2 run m3pro_teacher_vision qr_code_reader_node \
  --ros-args -p camera_topic:=/camera/rgb/image_raw/compressed

Logs obtenus :

QR reader ready: camera=/camera/rgb/image_raw/compressed, output=/qr_code, service=/qr/read

Mais le QR n'est pas détecté.

Le service répond :

success=False, message='No QR code detected yet'

Problème constaté :

ros2 topic hz /camera/color/image_raw

ne donne aucun résultat.

À vérifier :

- si la caméra publie vraiment des images ;
- si /camera/color/image_raw a un publisher ;
- si le topic compressed reçoit des frames ;
- si app_camera.launch.py est bien lancé ;
- vérifier /dev/video* ;
- tester rqt_image_view ou RViz Image.

Commandes utiles :

ros2 topic list | grep camera
ros2 topic info /camera/color/image_raw -v
ros2 topic hz /camera/color/image_raw --qos-profile sensor_data
ros2 topic hz /camera/rgb/image_raw/compressed
ls -l /dev/video*
ros2 node list | grep -i camera

## SLAM / Nav2

Anciennes maps déplacées dans :

/root/maps_backup/

Le dossier maps a été nettoyé.

Relance SLAM :

ros2 launch m3pro_teacher_nav slam_online.launch.py

Sauvegarde nouvelle map :

ros2 run nav2_map_server map_saver_cli -f /root/m3pro_teacher_ws/src/m3pro_teacher_nav/maps/salle_jury

Relance Nav2 :

ros2 launch m3pro_teacher_nav navigation.launch.py \
  map:=/root/m3pro_teacher_ws/src/m3pro_teacher_nav/maps/salle_jury.yaml \
  rviz:=true
