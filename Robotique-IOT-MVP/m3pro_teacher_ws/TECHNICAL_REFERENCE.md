# Technical Reference - Architecture & Key Concepts

## 1. Architecture Générale du Système

```
┌─────────────────────────────────────────────────────────────┐
│                    Yahboom M3 Pro Robot                     │
│                  (Jetson Nano / NX dans Docker)             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Sensors              Drivers         ROS2 Nodes           │
│  ═══════════════════════════════════════════════════════   │
│  • 2x Lidar 180°  →  Lidar driver  →  /scan0, /scan1      │
│  • RGB-D Camera   →  Camera driver →  /camera/*            │
│  • Encodeurs      →  Motor driver  →  /odom_raw           │
│  • Arm 6-DOF      →  Arm driver    →  /arm6_joints        │
│                                                             │
│  Processing Nodes                                           │
│  ═══════════════════════════════════════════════════════   │
│  • sensor_fusion_rgb_demo    → /teacher/scan_merged        │
│  • slam_toolbox              → /map, /tf (map→odom)        │
│  • controller_server (Nav2)  → motion planning             │
│  • planner_server (Nav2)     → path computation            │
│  • object_detector_node      → /teacher/detections         │
│  • pick_and_place_node       → arm IK, gripper control     │
│                                                             │
│  Communication Bridges                                      │
│  ═══════════════════════════════════════════════════════   │
│  • rosbridge_websocket       → port 9090 (WebSocket JSON)  │
│  • web_server_node           → port 8080 (HTTP/MJPEG)      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ Network (10.10.221.0/24)
                              │
┌─────────────────────────────────────────────────────────────┐
│              Your Computer / Browser                         │
│              10.10.221.XXX                                   │
├─────────────────────────────────────────────────────────────┤
│  • RViz 2            (local ROS2)                           │
│  • Web Dashboard     (http://10.10.221.123:8080)            │
│  • Terminal SSH      (ros2 commands)                        │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Frame TF Hierarchy

```
map (fixed frame = carte globale)
 │
 ├─ odom (odometry frame = point de départ)
 │   │
 │   ├─ base_link (centre du robot)
 │       │
 │       ├─ camera_link
 │       │   └─ camera_color_optical_frame (Z avant, Y bas)
 │       │
 │       ├─ scan0_frame (lidar avant)
 │       ├─ scan1_frame (lidar arrière)
 │       │
 │       └─ arm_base_link
 │           ├─ shoulder_pan_link
 │           ├─ upper_arm_link
 │           ├─ forearm_link
 │           ├─ wrist_pitch_link
 │           ├─ wrist_roll_link
 │           └─ gripper_palm_link
 │               ├─ left_finger_link
 │               └─ right_finger_link

Publisher des transformations:
  • SLAM  : map → odom (corrige dérive odométrie)
  • odom_raw_bridge : odom → base_link (depuis /odom_raw)
  • robot_state_publisher : base_link → others (URDF)
  • Bras driver : base_link → arm chain
```

---

## 3. Topics Critiques et Flux

### A. SLAM Loop

```
/scan0 ─────┐
            │
/scan1 ─────┼─→ sensor_fusion_rgb_demo ─→ /teacher/scan_merged (360°)
            │                                    │
/odom_raw → odom_raw_bridge → /odom + TF odom→base_link
/odom ──────────────────────────────────────────┼──→ slam_toolbox
                                                │      │
                                    ┌───────────┘      │
                                    │         ┌────────┴─────────┐
                                    │         │                  │
                              /map (OccupancyGrid)         /tf (map→odom)
```

**Paramètres clés** (`slam_toolbox_params.yaml`):
- `resolution: 0.05` → 5cm par cellule
- `do_loop_closing: true` → détecte revisites
- `scan_topic: /teacher/scan_merged` → 360° requis
- `base_frame: base_link` → frame robot utilisée pour SLAM/Nav2

Note terrain: le conteneur Yahboom publie l'odométrie sur `/odom_raw`. Le node
`m3pro_teacher_demos/odom_raw_bridge` crée `/odom` et la TF `odom → base_link`.

### B. Navigation Loop

```
User goal (RViz ou web)
    │
    ↓
Nav2 bt_navigator
    │
    ├─→ AMCL (localise robot avec filtre à particules)
    │      Utilise: /teacher/scan_merged, /odom
    │
    ├─→ planner_server (planification globale A*)
    │      Utilise: /map (OccupancyGrid)
    │
    ├─→ controller_server (suivi de chemin local)
    │      Utilise: /teacher/scan_merged (obstacles locaux)
    │
    └─→ behavior_server (gère blocages)
           Publie: /cmd_vel (Twist)
           Consomme: motion_base driver
```

**Costmaps**:
```
global_costmap:
  - layer: static_map  (de /map)
  - layer: inflation   (dégradé autour obstacles)
  Cost: 0 (libre) ... 254 (collision) 255 (inconnu)

local_costmap:
  - layer: observation (du lidar live)
  - layer: inflation
  Fenêtre glissante de 4m x 4m autour du robot
```

### C. Vision Loop

```
/camera/color/image_raw ──┐
                          ├─→ object_detector_node
/camera/depth/image_raw ──┘        │
                              ┌────┴──────────────────────┐
                              │                           │
                        /teacher/detections       /teacher/detection_image
                        (PoseArray 3D)            (annotated RGB)
                              │
                              ↓
                        pick_and_place_node
                              │
                        1. TF lookup:
                           camera_color_optical_frame → base_link
                              │
                        2. Compute IK (forward kinematics inverse)
                           (base_link x,y,z) → (θ1, θ2, ..., θ6)
                              │
                        3. Arm control
                           pub /arm_control (servo angles)
                           pub /cmd_vel (approach)
```

---

## 4. State Machine: Pick & Place

```
IDLE (attente)
  │
  ├─ Détection: objet trouvé
  ↓
APPROACH (conduire l'approche)
  │
  ├─ Distance < approach_dist (30cm)
  ├─ Robot: publie /cmd_vel
  ↓
REACH (déployer le bras)
  │
  ├─ Bras: 5cm au-dessus de l'objet (2s)
  ├─ Puis: descendre vers l'objet
  ├─ Robot: publie /arm6_joints (IK solution)
  ↓
GRASP (saisir)
  │
  ├─ Gripper: ferme à gripper_close_value (75°)
  ├─ Durée: 1s
  ↓
LIFT (relever)
  │
  ├─ Bras: remonte en position repos
  ├─ Durée: 2s
  ↓
DONE (terminé)
  │
  └─→ IDLE (retour)
```

**Timeouts**:
- APPROACH: 30s max (sinon abort)
- REACH: 2s
- GRASP: 1s
- LIFT: 2s

---

## 5. Détection HSV - Processus

```
Image RGB (640x480)
    ↓
Conversion RGB → HSV
    │
    H: Hue         [0-180°]   (teinte, robuste à l'éclairage)
    S: Saturation  [0-255]    (pureté)
    V: Value       [0-255]    (luminosité)
    │
    ↓
Masque binaire (deux plages HSV pour gérer le rouge)
    H ∈ [0,10] ∪ [170,180]
    S > 120, V > 70
    │
    ↓
Nettoyage morphologique
    • OPEN (éliminer bruit petit)
    • CLOSE (boucher trous)
    │
    ↓
Détection contours
    • Filtrer par aire (min_contour_area = 500 px²)
    │
    ↓
Rétro-projection 3D
    Pour chaque objet détecté:
      - Centroïde en pixels: (cx, cy)
      - Profondeur Z: lire dans l'image depth
      - Calcul 3D:
        x = (cx - cx_camera) / fx * Z
        y = (cy - cy_camera) / fy * Z
        z = Z
      - Frame: camera_color_optical_frame
```

**Paramètres critiques** (`detection_params.yaml`):
```yaml
hsv_low_1:  [0, 120, 70]      # Rouge bas (0-10°)
hsv_high_1: [10, 255, 255]
hsv_low_2:  [170, 120, 70]    # Rouge haut (170-180°)
hsv_high_2: [180, 255, 255]

min_contour_area: 500         # pixels²
max_detection_depth: 1.0      # mètres
camera_fx: 615.0              # pixels (intrinsèques)
camera_fy: 615.0
camera_cx: 320.0
camera_cy: 240.0
depth_scale: 0.001            # raw → mètres
```

---

## 6. Cinématique Inverse (IK) du Bras

```
Position cible en base_link: (x, y, z)
    ↓
Étape 1: Rotation de base
    base_yaw = atan2(y, x)
    └→ Tourne le bras pour pointer vers (x,y)
    │
Étape 2: Géométrie planaire 2-segment (vue de côté)
    Distance horizontale: r = √(x² + y²)
    Hauteur relative: h = z - arm_base_z (0.24m)
    │
    Segments: L1 (bras haut) = 0.11m
              L2 (avant-bras) = 0.11m
    │
    Théorème d'Al-Kashi:
    ┌─────────────────────────────────────────────────┐
    │ cos(θ2) = (L1² + L2² - d²) / (2·L1·L2)          │
    │ où d = √(r² + h²)                              │
    │                                                 │
    │ θ1 = atan2(h,r) + acos((L1²+d²-L2²)/(2·L1·d)) │
    │ θ2 = acos(...) - π                             │
    └─────────────────────────────────────────────────┘
    │
Étape 3: Compensation du poignet
    wrist_pitch = -(θ1 + θ2) - π/2
    └→ Pince pointe vers le bas malgré l'inclinaison
    │
Résultat: [base_yaw, shoulder_joint, elbow_joint, wrist_pitch, ...]
    (angles en radians)
    │
Conversion Yahboom
    servo_degrees = radians * (180/π) + 90
    └→ 90° = position centrale
```

**Cas d'échec IK**:
- Objet hors portée (distance > L1 + L2 ≈ 0.34m)
- Angles dépassent limites articulaires (±1.57 rad)
- Position impossible géométriquement

---

## 7. Web Architecture

```
┌─────────────────────────────────────────────────────┐
│              Web Browser (votre PC)                  │
│              http://10.10.221.123:8080               │
├─────────────────────────────────────────────────────┤
│  index.html (JavaScript)                            │
│  • ROS client (roslibjs)                            │
│  • Canvas pour la carte                             │
│  • Connexion WebSocket                              │
│  • Listeners des topics ROS                         │
└─────────────────────────────────────────────────────┘
           │                              │
           │ HTTP GET/POST                │ WebSocket (port 9090)
           │                              │
      ┌────▼─────────────────────────────▼──────────────┐
      │         Jetson (10.10.221.123)                  │
      │                                                 │
      ├─ web_server_node (port 8080)                   │
      │  ├─ Serve static files (index.html, CSS)       │
      │  ├─ /camera/snapshot endpoint (JPEG)           │
      │  └─ /camera/stream endpoint (MJPEG)            │
      │                                                 │
      ├─ rosbridge_websocket (port 9090)               │
      │  └─ Convertit ROS messages ↔ JSON              │
      │                                                 │
      └─ ROS2 Topics                                    │
         ├─ /map (OccupancyGrid)      → canvas         │
         ├─ /odom (Odometry)          → stats          │
         ├─ /teacher/detections       → display        │
         ├─ /teacher/camera_*         → images         │
         └─ /goal_pose (reçoit)       ← clics user     │
```

**Flux Image Caméra**:
```
Mode "Live Camera":
  Caméra USB → web_server_node (compresse JPEG) → /camera/snapshot
  Navigateur: GET /camera/snapshot chaque 150ms → affiche MJPEG

Mode "Object Detection" (annoté):
  Caméra → object_detector_node → /teacher/detection_image (Image ROS)
  rosbridge → WebSocket JSON → Canvas JavaScript

Latence estimée: 150-200ms (network + compression)
```

---

## 8. Checklist Diagnostic - Si Ça ne Marche Pas

### A. Pas de topics visibles?
```bash
# Vérifiez le bringup Yahboom
ros2 node list
ros2 node info /yahboomcar_driver
```

### B. SLAM ne construit pas la carte?
```bash
# Vérifiez que le scan est reçu
ros2 topic hz /teacher/scan_merged  # doit être ~10 Hz
# Bougez le robot, attendez 10s minimum
# Vérifiez /map
ros2 topic info /map
```

### C. Navigation ne fonctionne pas?
```bash
# 1. Relancez AMCL (2D Pose Estimate dans RViz)
# 2. Vérifiez la localisation
ros2 topic echo /amcl_pose --once
# 3. Vérifiez les costmaps
ros2 topic echo /global_costmap/costmap --once
```

### D. Détection ne voit rien?
```bash
# Ouvrez l'image brute
ros2 run rqt_image_view rqt_image_view /camera/color/image_raw
# Placez un objet rouge devant
# Regardez les histogrammes HSV
# Ajustez detection_params.yaml
```

### E. Bras ne bouge pas?
```bash
# Vérifiez le topic
ros2 topic list | grep arm
# Probablement: /arm_control ou /servo_control
# Mettez à jour arm_command_topic dans detection_params.yaml
```

---

## 9. Performance Metrics

| Composant | Fréquence | Latence | Notes |
|-----------|-----------|---------|-------|
| Lidar avant (`/scan0`) | 10 Hz | ~50ms | 270 points |
| Lidar arrière (`/scan1`) | 10 Hz | ~50ms | 270 points |
| Odométrie brute (`/odom_raw`) | 20-50 Hz | ~20ms | IMU + encodeurs Yahboom |
| Odométrie standard (`/odom`) | 20-50 Hz | ~20ms | Publiée par `odom_raw_bridge` |
| RGB Camera | ~30 Hz | ~33ms | 640x480 |
| Depth Camera | ~30 Hz | ~33ms | 640x480 |
| SLAM (`/map`) | 0.33 Hz | ~3s | Computation time |
| Nav2 (`/cmd_vel`) | 10 Hz | ~100ms | path tracking |
| Object detection | 10 Hz | ~100ms | OpenCV processing |
| Arm servo response | ~50 Hz | ~20ms | Physical servo |
| Web dashboard | ~6 FPS | ~150ms | Network + browser |

---

## 10. Ressources Utilisées

- **CPU**: Jetson Nano (4 cores) / Jetson NX (6 cores)
- **RAM**: ~2-3 GB active (ROS2 + Docker)
- **Storage**: ~500MB workspace + 50MB carte pour salle small
- **Network**: Wi-Fi 2.4GHz (recommandé 5GHz pour fiabilité)
- **Puissance**: ~15W (lidar), ~5W (caméra), ~20W (moteurs), ~10W (CPU) = ~50W total

---

**Version**: 1.0 | **Date**: May 2026 | **For**: M3 Pro Teacher Exercise
