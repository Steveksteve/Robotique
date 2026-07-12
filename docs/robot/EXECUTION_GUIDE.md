# Guide d'Exécution - Exercice SLAM, Nav2 et Pick & Place

## [OK] État du Repo

### Code Quality
- **FIXED**: Bug dans `pick_and_place_node.py` - fonction `quat_rotate` avait deux implémentations conflictuelles
- **VERIFIED**: Configurations SLAM, Nav2, Vision OK
- **VERIFIED**: Launch files OK
- **VERIFIED**: Tous les 5 packages présents et compilables

### Architecture Validée
```
Yahboom M3 Pro (10.10.221.123)
├── Docker + ROS2 Humble
├── Sensors: 2x Lidar 180° + RGB-D Camera
├── Arm: 6 DOF + Gripper
└── Workspace: /root/m3pro_teacher_ws
```

---

##  EXÉCUTION ÉTAPE PAR ÉTAPE

### Phase 1: PRÉPARATION (SSH → Jetson)

Depuis le **PC Ubuntu/WSL**, assurez-vous d'abord que l'agent Jetson tourne, puis déployez le workspace vers le robot et le conteneur Docker:

```bash
ssh jetson@10.10.221.123 'bash /home/jetson/start_agent.sh'

cd /mnt/c/hetic/aaaa/m3pro_teacher_ws
CONTAINER=infallible_kare ./scripts/deploy_workspace_to_robot.sh 10.10.221.123
```

Ce script copie le projet vers `/home/jetson/m3pro_teacher_ws`, le copie ensuite dans Docker vers `/root/m3pro_teacher_ws`, puis lance `colcon build --symlink-install` dans le conteneur.

Pour ouvrir un shell ROS sur le robot:

```bash
# 1. Connectez-vous au robot
ssh jetson@10.10.221.123

# 2. Lancez l'agent Jetson du robot
bash /home/jetson/start_agent.sh

# 3. Entrez dans le conteneur Docker ROS2
docker exec -it \
  -e ROS_DOMAIN_ID=30 \
  -e FASTDDS_BUILTIN_TRANSPORTS=UDPv4 \
  -e DISPLAY=:0 \
  infallible_kare \
  bash

# 4. Dans le conteneur, sourcez les workspaces
source /opt/ros/humble/setup.bash
source /root/yahboomcar_ws/install/setup.bash 2>/dev/null || true
source /root/M3Pro_ws/install/setup.bash 2>/dev/null || true
source /root/m3pro_teacher_ws/install/setup.bash

# 5. Vérifiez les paquets
ros2 pkg list | grep m3pro_teacher
# Résultat attendu:
# m3pro_teacher_demos
# m3pro_teacher_description
# m3pro_teacher_nav
# m3pro_teacher_vision
# m3pro_teacher_web
```

### Phase 2: DÉMARRAGE - VÉRIFICATIONS (Terminal bringup)

```bash
# Le bringup Yahboom doit TOUJOURS tourner
# Il publie: /scan0, /scan1, /odom_raw, /cmd_vel, topics caméra, driver bras
# Le workspace fournit odom_raw_bridge: /odom_raw -> /odom + TF odom -> base_link
# (détails: voir documentation Yahboom)

# VÉRIFICATION: Topics critiques actifs
ros2 topic hz /scan0          # ~10 Hz
ros2 topic hz /odom_raw       # ~20-50 Hz
ros2 topic hz /camera/color/image_raw  # ~30 Hz
```

---

## PARTIE A: SLAM — Construire une Carte

### A.1. Terminal 1: Lancer SLAM online

```bash
ros2 launch m3pro_teacher_nav slam_online.launch.py
```

**Attendez**: RViz s'ouvre, robot au centre, scan laser vert autour.

### A.2. Terminal 2: Téléopération

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

**Consignes**:
- Roulez **lentement** (0.10-0.15 m/s)
- Longez les murs à ~50 cm
- Faites une **boucle complète**
- Revenez au point de départ (fermeture de boucle)
- Durée: 2-3 minutes pour une petite salle

### A.3. Terminal 3: Sauvegarder la carte

```bash
source /opt/ros/humble/setup.bash
ros2 run nav2_map_server map_saver_cli \
  -f /root/m3pro_teacher_ws/src/m3pro_teacher_nav/maps/salle
```

**Vérifiez**:
```bash
ls -la /root/m3pro_teacher_ws/src/m3pro_teacher_nav/maps/
# → salle.pgm (image)
# → salle.yaml (métadonnées)
```

Pour récupérer la carte sur votre PC:

```bash
ssh jetson@10.10.221.123 \
'docker cp infallible_kare:/root/m3pro_teacher_ws/src/m3pro_teacher_nav/maps /home/jetson/maps'

scp -r jetson@10.10.221.123:/home/jetson/maps ./maps
```

[OK] **Checkpoint A complété**: Carte sauvegardée

---

## PARTIE B: Navigation Autonome (Nav2)

### B.1. Terminal 1: Arrêtez SLAM + lancez Nav2

```bash
# Ctrl-C dans le terminal SLAM
# Puis:
ros2 launch m3pro_teacher_nav navigation.launch.py \
  map:=/root/m3pro_teacher_ws/src/m3pro_teacher_nav/maps/salle.yaml
```

### B.2. Terminal 2: Localisation (RViz)

AMCL ne publie `map → odom` qu'après réception d'une pose initiale. Tant que cette pose n'est pas donnée, RViz peut afficher `Frame [map] does not exist` ou des messages `Message Filter dropping message`.

1. Cliquez **"2D Pose Estimate"** dans RViz
2. Cliquez sur la carte **là où le robot se trouve réellement**
3. Glissez pour indiquer la direction

**Attendez**: Les particules vertes convergent

Si le bouton RViz ne suffit pas, forcez une pose initiale en ligne de commande:

```bash
ros2 topic pub --once /initialpose geometry_msgs/msg/PoseWithCovarianceStamped \
"{header: {frame_id: 'map'}, pose: {pose: {position: {x: 0.0, y: 0.0, z: 0.0}, orientation: {w: 1.0}}, covariance: [0.25, 0, 0, 0, 0, 0, 0, 0.25, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.0685]}}"
```

Vérification:

```bash
ros2 run tf2_ros tf2_echo odom base_link
ros2 run tf2_ros tf2_echo map odom
```

La chaîne attendue est `map → odom → base_link`.

### B.3. Terminal 2: Envoyer un objectif (RViz)

1. Cliquez **"2D Goal Pose"** (touche `G`)
2. Cliquez sur la carte
3. Le robot navigue autonomement

**Observez**: `/cmd_vel` change, le robot suit le chemin, évite les obstacles

[OK] **Checkpoint B complété**: Navigation autonome fonctionnelle

---

## PARTIE C: Tableau de Bord Web

### C.1. Terminal 3: Lancez le web dashboard

```bash
ros2 launch m3pro_teacher_web web_dashboard.launch.py
```

### C.2. Sur votre ordinateur

Ouvrez un navigateur:
```
http://10.10.221.123:8080
```

**Vérifiez**:
- [OK] Connexion "CONNECTED" (vert)
- [OK] Carte visible
- [OK] Caméra active
- [OK] État du robot affiché

[OK] **Checkpoint C complété**: Dashboard accessible

---

## PARTIE D: Détection Visuelle (HSV)

### D.1. Terminal 4: Lancez la détection seule

```bash
ros2 launch m3pro_teacher_vision detect_and_pick.launch.py pick:=false
```

### D.2. Placez un objet ROUGE (15 cm - 1 m devant la caméra)

**Observez les logs**:
```
[INFO] Detected 1 object(s), nearest at (0.45, 0.05, 0.12)m
```

### D.3. Vérifiez les topics

```bash
# Terminal supplémentaire:
ros2 topic echo /teacher/detections
# → positions 3D de l'objet dans camera_color_optical_frame
```

**Visualisez l'image annotée**:
```bash
ros2 run rqt_image_view rqt_image_view /teacher/detection_image
# → cercle vert autour de l'objet
```

[OK] **Checkpoint D complété**: Détection fonctionnelle

---

## PARTIE E: Pick & Place (AVEC AUTORISATION ENSEIGNANT)

### Attention : ATTENTION: Le bras va bouger

### E.1. Terminal 4: Lancez pick & place

```bash
# Remplacez pick:=false par pick:=true
ros2 launch m3pro_teacher_vision detect_and_pick.launch.py pick:=true
```

### E.2. Placez un objet ROUGE au sol (30 cm - 1 m)

**Le robot doit**:
1. Détecter l'objet
2. Rouler vers lui (APPROACH)
3. Déployer le bras (REACH)
4. Fermer la pince (GRASP)
5. Relever le bras (LIFT)
6. Retourner à l'attente (DONE)

**Observez les logs**:
```
[INFO] Target acquired at base_link (0.30, 0.05, 0.02). Approaching...
[INFO] State: APPROACH -> REACH
[INFO] State: REACH -> GRASP
[INFO] State: GRASP -> LIFT
[INFO] Pick complete! Returning to IDLE.
```

[OK] **Checkpoint E complété**: Pick & Place fonctionnel

---

## PARTIE F: Intégration Complète

### F.1. Lancez **4 terminaux** simultanément

**Terminal 1 - Bringup** (si pas déjà lancé):
```bash
bash /home/jetson/start_agent.sh
```

**Terminal 2 - SLAM + Navigation**:
```bash
ros2 launch m3pro_teacher_nav slam_and_nav.launch.py
```

**Terminal 3 - Web Dashboard**:
```bash
ros2 launch m3pro_teacher_web web_dashboard.launch.py
```

**Terminal 4 - Détection + Pick**:
```bash
ros2 launch m3pro_teacher_vision detect_and_pick.launch.py pick:=true
```

### F.2. Scénario: Exploration + Ramassage

1. **Dans le web dashboard** (http://10.10.221.123:8080):
   - Cliquez sur un point de la carte
   - Cliquez "Send Nav Goal"

2. **Le robot**:
   - Explore la région
   - Construit la carte en temps réel
   - Détecte les objets rouges automatiquement
   - Les ramasse

3. **Observez le workflow**:
   - Carte se construit
   - Caméra active dans le dashboard
   - Pick & Place logs en temps réel

[OK] **Checkpoint F complété**: Système complet intégré

---

## PARTIE G: Nettoyage

### G.1. Arrêtez tous les terminaux

```bash
# Dans chaque terminal (ordre inverse de lancement):
Ctrl-C dans Terminal 4 (detection + pick)
Ctrl-C dans Terminal 3 (web)
Ctrl-C dans Terminal 2 (SLAM/Nav2)
Ctrl-C dans Terminal 1 (bringup)
```

### G.2. Ramenez le robot à l'arrêt

```bash
# Publiez une commande nulle
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 0.0}, angular: {z: 0.0}}"
```

### G.3. Ramenez le bras au repos

```bash
# Ramenez tous les servos à la position centrale (90°)
ros2 topic pub --once /arm6_joints arm_msgs/msg/ArmJoints \
  "{joint1: 90, joint2: 120, joint3: 10, joint4: 20, joint5: 90, joint6: 30, time: 700}"
```

### G.4. Vérifiez qu'il n'y a pas de processus orphelins

```bash
ps aux | grep -E 'slam_toolbox|rviz2|rosbridge' | grep -v grep
```

**Fin de l’exercice**

---

##  Troubleshooting

| Problème | Solution |
|----------|----------|
| Bras ne bouge pas | Vérifiez `/arm_control` topic, installer `arm_msgs` |
| Détection ne marche pas | Testez HSV tunning avec `rqt_image_view`, ajustez couleur |
| `Frame [map] does not exist` dans RViz | Lancez `navigation.launch.py`, attendez `/amcl`, puis faites "2D Pose Estimate" ou publiez `/initialpose` |
| `odom` n'existe pas | Vérifiez `/odom_raw`, puis `ros2 run m3pro_teacher_demos odom_raw_bridge` |
| Nav2 ignore les murs | Relancez AMCL avec "2D Pose Estimate" |
| Caméra noire | Vérifiez Yahboom bringup camera launching |
| Dashboard pas accessible | Vérifiez firewall, adresse IP, port 8080 |

---

##  Checkpoints de Réussite

- [ ] Checkpoint A: Carte SLAM sauvegardée
- [ ] Checkpoint B: Robot navigue autonomement
- [ ] Checkpoint C: Dashboard web accessible
- [ ] Checkpoint D: Objets détectés en HSV
- [ ] Checkpoint E: Bras effectue pick & place
- [ ] Checkpoint F: Intégration complète fonctionne

**Condition de réussite : tous les checkpoints sont validés.**

---

##  Références Utiles

- Configuration SLAM: `src/m3pro_teacher_nav/config/slam_toolbox_params.yaml`
- Configuration Nav2: `src/m3pro_teacher_nav/config/nav2_params.yaml`
- Paramètres détection: `src/m3pro_teacher_vision/config/detection_params.yaml`
- Code pick & place: `src/m3pro_teacher_vision/m3pro_teacher_vision/pick_and_place_node.py`

---

