# 🚀 Quick Reference - M3 Pro SLAM/Nav2/Vision Exercise

## ⚡ 60-Second Setup

```bash
# Local Docker build only, from your PC:
cd /mnt/c/hetic/aaaa/m3pro_teacher_ws
docker build -t m3pro_teacher_ws:humble .

# Or:
docker compose run --build --rm m3pro_teacher_build

# From your PC Ubuntu/WSL: deploy + build in Docker
ssh jetson@10.10.221.123 'bash /home/jetson/start_agent.sh'

cd /mnt/c/hetic/aaaa/m3pro_teacher_ws
CONTAINER=infallible_kare ./scripts/deploy_workspace_to_robot.sh 10.10.221.123

# On Jetson
ssh jetson@10.10.221.123
bash /home/jetson/start_agent.sh

# Then enter Docker
docker exec -it -e ROS_DOMAIN_ID=30 -e FASTDDS_BUILTIN_TRANSPORTS=UDPv4 -e DISPLAY=:0 infallible_kare bash
source /opt/ros/humble/setup.bash
source /root/m3pro_teacher_ws/install/setup.bash

# 4 terminals simultaneously:
# T1: bash /home/jetson/start_agent.sh  (Jetson/Yahboom agent)
# T2: ros2 launch m3pro_teacher_nav slam_and_nav.launch.py
# T3: ros2 launch m3pro_teacher_web web_dashboard.launch.py  
# T4: ros2 launch m3pro_teacher_vision detect_and_pick.launch.py pick:=true

# On your computer:
http://10.10.221.123:8080
```
SSH:  ssh jetson@10.10.221.123
VNC:  vnc://10.10.221.123:5900
HTTP: http://10.10.221.123:8080
---

## 🎯 Exercise Phases (7 Total)

| Phase | Goal | Time | Commands |
|-------|------|------|----------|
| **A** | SLAM - Build map | 10min | `slam_online.launch.py` + teleop |
| **B** | Nav2 - Navigate | 5min | `navigation.launch.py` + RViz goals |
| **C** | Web - Dashboard | 2min | `web_dashboard.launch.py` |
| **D** | Vision - Detect | 3min | `detect_and_pick.launch.py pick:=false` |
| **E** | Pick - Grasp objects | 5min | `detect_and_pick.launch.py pick:=true` |
| **F** | Integration - Full system | 10min | All 4 terminals |
| **G** | Cleanup - Stop all | 2min | `Ctrl-C` x4 |

**Total**: ~40 minutes

---

## 📊 Key Parameters

### SLAM
```yaml
resolution: 0.05          # 5cm per cell (good for indoors)
do_loop_closing: true     # detects revisits
max_laser_range: 3.5      # meters
scan_topic: /teacher/scan_merged  # 360° required
base_frame: base_link
odom_frame: odom          # created from /odom_raw by odom_raw_bridge
```

### Nav2
```yaml
max_vel_x: 0.20           # m/s (prudent)
max_vel_theta: 0.8        # rad/s
xy_goal_tolerance: 0.15   # meters (15cm accuracy)
yaw_goal_tolerance: 0.25  # radians
```

### Vision
```yaml
hsv_low_1: [0, 120, 70]         # Red range 1
hsv_high_1: [10, 255, 255]
hsv_low_2: [170, 120, 70]       # Red range 2 (hue wraps)
min_contour_area: 500           # pixels²
camera_fx: 615.0                # intrinsics (RealSense D435)
```

### Pick & Place
```yaml
approach_distance: 0.30   # Stop 30cm from object
gripper_open_value: 30    # servo degrees
gripper_close_value: 75
upper_arm_length: 0.11    # meters
forearm_length: 0.11
```

---

## 🔍 Debug Commands

```bash
# Verify sensors
ros2 topic hz /scan0                    # ~10 Hz
ros2 topic hz /odom_raw                 # ~20-50 Hz from Yahboom
ros2 topic hz /odom                     # ~20-50 Hz after odom_raw_bridge
ros2 topic hz /camera/color/image_raw   # ~30 Hz

# Verify TF
ros2 run tf2_ros tf2_echo odom base_link
ros2 run tf2_ros tf2_echo map odom      # after AMCL initial pose

# Check map
ros2 topic echo /map --once             # OccupancyGrid?

# Verify detection
ros2 topic echo /teacher/detections     # PoseArray 3D?
ros2 run rqt_image_view rqt_image_view /teacher/detection_image

# Monitor arm (when running pick_and_place)
ros2 topic echo /arm6_joints            # Joint angles?

# Check web
curl -s http://10.10.221.123:8080 | head -c 100
```

---

## 🎮 RViz Shortcuts

| Action | Key / Button |
|--------|--------------|
| Set Nav Goal | `G` or "2D Goal Pose" button |
| Set Initial Pose | Ctrl+G or "2D Pose Estimate" button |
| Rotate View | Middle-click + drag |
| Pan View | Shift + right-click + drag |
| Zoom | Scroll |
| Reset View | `R` |

---

## 📡 Topic Reference

### From Sensors
```
/scan0                      LaserScan (front, 180°)
/scan1                      LaserScan (rear, 180°)
/odom_raw                   Odometry brute Yahboom
/camera/color/image_raw     Image RGB (640x480)
/camera/depth/image_raw     Image depth (mono16)
```

### From Processing
```
/odom                       Odometry standard from odom_raw_bridge
/teacher/scan_merged        LaserScan (360° fused)
/map                        OccupancyGrid (from SLAM)
/teacher/detections         PoseArray (object positions 3D)
/teacher/detection_image    Image (annotated)
```

### Commands
```
/cmd_vel                    Twist (to motors)
/goal_pose                  PoseStamped (Nav2 goal)
/arm_control               ArmJoints (to arm driver)
```

---

## ⚠️ Common Issues & Fixes

| Problem | Fix |
|---------|-----|
| **Bringup not found** | Ensure Yahboom ROS2 packages installed |
| **Lidar topics empty** | Restart lidar driver or Docker container |
| **SLAM no map update** | Move robot slowly, wait 5-10s, check hz |
| **`odom` frame missing** | Check `/odom_raw`, rebuild, then run `ros2 run m3pro_teacher_demos odom_raw_bridge` |
| **`map` frame missing in RViz** | In Nav2, set initial pose with RViz "2D Pose Estimate" or publish `/initialpose` |
| **Nav2 overshoots goal** | Increase xy_goal_tolerance slightly |
| **Object not detected** | Use rqt_image_view, check HSV range |
| **Arm not moving** | Verify arm_command_topic in config |
| **Web dashboard blank** | Check 10.10.221.123 IP, ping Jetson |
| **Camera black in web** | Restart web_server_node, check perms |

---

## 📚 Document References

- **EXECUTION_GUIDE.md** ← Main step-by-step guide (start here!)
- **PREPARATION_CHECKLIST.md** ← Pre-flight verification
- **TECHNICAL_REFERENCE.md** ← Architecture deep-dive
- **EXO_SLAM_NAV_BRAS.md** ← Original exercise text with questions

---

## ✅ Success Criteria

### Phase A (SLAM)
- [ ] Carte construite sans trous visibles
- [ ] Fichiers salle.pgm et salle.yaml créés
- [ ] AMCL converge sur la carte

### Phase B (Nav2)
- [ ] Robot suit les chemins dans RViz
- [ ] Évite les obstacles
- [ ] Arrive aux objectifs ±15cm

### Phase C (Web)
- [ ] Dashboard accessible
- [ ] Carte affichée
- [ ] Caméra en direct

### Phase D (Vision)
- [ ] Objet rouge détecté
- [ ] Positions 3D correctes
- [ ] Image annotée montre le cercle

### Phase E (Pick)
- [ ] Robot s'approche
- [ ] Bras se déploie
- [ ] Pince se ferme
- [ ] Bras se relève

### Phase F (Integration)
- [ ] Tous les systèmes en même temps
- [ ] Workflows complets

---

## 🎓 Learning Outcomes

After this exercise, you will understand:
- ✓ How SLAM builds maps using lidar + odometry
- ✓ How loop closure corrects cumulative drift
- ✓ How AMCL localizes a robot on a known map
- ✓ How Nav2 plans and tracks paths
- ✓ How costmaps prevent collisions
- ✓ How color-space (HSV) improves object detection
- ✓ How inverse kinematics controls the arm
- ✓ How ROS2 systems integrate sensors, algorithms, and UI
- ✓ How WebSockets bridge ROS2 to web browsers

---

## 🔗 Useful Links

- [ROS 2 Documentation](https://docs.ros.org)
- [Nav2 Tutorials](https://navigation.ros.org)
- [slam_toolbox](https://github.com/StanleyLab/slam_toolbox)
- [OpenCV HSV](https://docs.opencv.org/master/df/d9d/tutorial_py_colorspaces.html)
- [Quaternion Math](https://en.wikipedia.org/wiki/Quaternions_and_spatial_rotation)

---

**Status**: ✅ Ready to Execute

**Last Updated**: May 2026

**Questions?** Check TECHNICAL_REFERENCE.md section 10 (Diagnostic Checklist)
