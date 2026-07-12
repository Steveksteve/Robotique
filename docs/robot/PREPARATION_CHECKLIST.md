# Checklist: Préparation du Workspace

## 1. Vérification des Packages ROS2

```bash
# Connectez-vous au Jetson et lancez l'agent robot
ssh jetson@10.10.221.123
bash /home/jetson/start_agent.sh

#sur le cmd depuis le robot:
docker start infallible_kare

# Entrez ensuite dans le conteneur ROS2
docker exec -it \
  -e ROS_DOMAIN_ID=30 \
  -e FASTDDS_BUILTIN_TRANSPORTS=UDPv4 \
  -e DISPLAY=:0 \
  infallible_kare \
  bash

# Sourcez ROS2
source /opt/ros/humble/setup.bash

# Vérifiez les packages système requis
ros2 pkg list | grep -E "slam_toolbox|nav2|rosbridge_server|tf2"
```

**Résultat attendu** (tous présents):
```
nav2_bringup
nav2_core
nav2_map_server
slam_toolbox
rosbridge_server
tf2
```

Si manquant, installez:
```bash
sudo apt update
sudo apt install -y \
  ros-humble-slam-toolbox \
  ros-humble-navigation2 \
  ros-humble-nav2-bringup \
  ros-humble-rosbridge-server
```

---

## 2. Compilation du Workspace

### Option locale: build Docker sur le PC

```bash
cd /mnt/c/hetic/aaaa/m3pro_teacher_ws
docker build -t m3pro_teacher_ws:humble .

# Alternative avec Compose
docker compose run --build --rm m3pro_teacher_build
```

Cette option vérifie que les 5 packages compilent dans une image ROS2 Humble propre. Elle ne remplace pas le déploiement dans le conteneur Yahboom du robot.

### Option robot: déploiement + build dans Docker Yahboom

Depuis le PC Ubuntu/WSL, déployez et compilez directement dans le conteneur du robot:

```bash
ssh jetson@10.10.221.123 'bash /home/jetson/start_agent.sh'

cd /mnt/c/hetic/aaaa/m3pro_teacher_ws
CONTAINER=infallible_kare ./scripts/deploy_workspace_to_robot.sh 10.10.221.123
```

Si vous êtes déjà dans le conteneur, compilez manuellement:

```bash
# Allez au workspace
cd /root/m3pro_teacher_ws

# Build
colcon build --symlink-install

# Sourcez
source install/setup.bash

# Vérifiez les 5 packages
ros2 pkg list | grep m3pro_teacher
```

**Résultat attendu**:
```
m3pro_teacher_demos
m3pro_teacher_description
m3pro_teacher_nav
m3pro_teacher_vision
m3pro_teacher_web
```

---

## 3. Vérification des Exécutables

```bash
# Vérifiez que tous les noeuds Python sont exécutables
ls -la /root/m3pro_teacher_ws/install/*/bin/

# Testez chaque exécutable (ne lancez pas, juste testez le import)
python3 -c "import m3pro_teacher_demos; print('[OK] m3pro_teacher_demos')"
python3 -c "import m3pro_teacher_vision; print('[OK] m3pro_teacher_vision')"
python3 -c "import m3pro_teacher_web; print('[OK] m3pro_teacher_web')"
```

**Résultat attendu**: 3 messages "[OK]"

---

## 4. Vérification des Capteurs

```bash
# Terminal 1: Vérifiez les topics du Yahboom bringup
ros2 topic list | head -20

# Vous devez voir (au minimum):
# /scan0                      (lidar avant)
# /scan1                      (lidar arrière)
# /odom_raw                   (odométrie Yahboom brute)
# /odom                       (créé par odom_raw_bridge)
# /cmd_vel                    (commande moteurs)
# /camera/color/image_raw     (caméra RGB)
# /camera/depth/image_raw     (caméra profondeur)
# /arm6_joints                (état du bras)
```

**Test de publication**:
```bash
# Vérifiez que les topics publient réellement
ros2 topic hz /scan0            # Doit afficher ~10 Hz
ros2 topic hz /odom_raw         # Doit afficher ~20-50 Hz
ros2 topic hz /odom             # Doit afficher ~20-50 Hz après lancement du bridge
ros2 topic hz /camera/color/image_raw  # Doit afficher ~30 Hz
```

---

## 5. Vérification des Transformations (TF)

```bash
# Vérifiez l'arbre TF
ros2 run tf2_tools view_frames.py
firefox frames.pdf &

# Ou directement dans le terminal:
ros2 run tf2_ros tf2_echo odom base_link
# Doit afficher une transformation changeante après odom_raw_bridge

ros2 run tf2_ros tf2_echo camera_color_optical_frame base_link
# Doit afficher une transformation stable
```

En navigation avec une carte sauvegardée, la TF `map → odom` apparaît seulement après la pose initiale AMCL (`2D Pose Estimate` dans RViz ou publication sur `/initialpose`).

---

## 6. Vérification des Configurations

```bash
# Vérifiez que les fichiers YAML existent
test -f /root/m3pro_teacher_ws/src/m3pro_teacher_nav/config/slam_toolbox_params.yaml && echo "[OK] SLAM config"
test -f /root/m3pro_teacher_ws/src/m3pro_teacher_nav/config/nav2_params.yaml && echo "[OK] Nav2 config"
test -f /root/m3pro_teacher_ws/src/m3pro_teacher_vision/config/detection_params.yaml && echo "[OK] Detection config"

# Vérifiez que la carte peut être créée
test -d /root/m3pro_teacher_ws/src/m3pro_teacher_nav/maps/ && echo "[OK] Maps directory"
```

**Résultat attendu**: 4 messages "[OK]"

---

## 7. Vérification des Dépendances Python

```bash
# Sur le Jetson (dans le conteneur)
python3 -c "import cv2; print('[OK] cv2')"
python3 -c "import numpy; print('[OK] numpy')"
python3 -c "import rclpy; print('[OK] rclpy')"
python3 -c "import tf2_geometry_msgs; print('[OK] tf2')"

# Si manquant, installez:
pip install opencv-python numpy
sudo apt install -y python3-tf2-geometry-msgs
```

---

## 8. Test de Lancement (sans bringup)

```bash
# Terminal 1: Lancez juste le sensor fusion (démonstration)
ros2 run m3pro_teacher_demos sensor_fusion_rgb_demo

# Terminal 2: Vérifiez le scan fusionné
ros2 topic echo /teacher/scan_merged --once
# Doit afficher un LaserScan avec 360 points environ

# Terminal 3: Arrêtez avec Ctrl-C
```

---

## 9. Vérification Finale - Mode Sec (Dry-run)

```bash
# Terminal 1: Lancez detection + pick & place (mode dry-run)
ros2 launch m3pro_teacher_vision detect_and_pick.launch.py pick:=false

# Terminal 2: Vérifiez qu'aucune erreur sur les topics
ros2 topic list | grep teacher

# Terminal 3: Lisez les logs
# Doit afficher "[INFO] Object detector started..."
# Doit afficher "[INFO] Pick-and-place controller ready (state: IDLE)"
```

---

## [OK] Checklist Finale

- [ ] Tous les packages ROS2 système installés
- [ ] Workspace compilé sans erreur
- [ ] Tous les 5 packages m3pro_teacher présents
- [ ] Tous les topics capteurs actifs
- [ ] Transformations TF correctes
- [ ] Fichiers de configuration YAML valides
- [ ] Dépendances Python installées
- [ ] Launch files lancements sans erreur
- [ ] Logs sans message "ERROR" ou "FATAL"

**Si tous les points sont [OK], le système est prêt pour l'exercice complet.**

---

##  Lancement Rapide (si tout est prêt)

```bash
# 4 terminaux Docker différents:

# Terminal 1: Bringup Yahboom
bash /home/jetson/start_agent.sh

# Terminal 1bis: Shell ROS dans Docker
docker exec -it -e ROS_DOMAIN_ID=30 -e FASTDDS_BUILTIN_TRANSPORTS=UDPv4 -e DISPLAY=:0 infallible_kare bash
source /opt/ros/humble/setup.bash
source /root/m3pro_teacher_ws/install/setup.bash

# Terminal 2: SLAM + Navigation
ros2 launch m3pro_teacher_nav slam_and_nav.launch.py

# Terminal 3: Web Dashboard
ros2 launch m3pro_teacher_web web_dashboard.launch.py

# Terminal 4: Détection + Pick
ros2 launch m3pro_teacher_vision detect_and_pick.launch.py pick:=true
```

Puis ouvrez: `http://10.10.221.123:8080`

---

**Statut** : Prêt pour l'exercice
