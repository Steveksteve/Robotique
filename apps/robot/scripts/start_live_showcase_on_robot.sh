#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROBOT_HOST="${ROBOT_HOST:-192.168.50.102}"
ROBOT_USER="${ROBOT_USER:-jetson}"
ROS_DOMAIN_ID="${ROS_DOMAIN_ID:-30}"
FASTDDS_BUILTIN_TRANSPORTS="${FASTDDS_BUILTIN_TRANSPORTS:-UDPv4}"
CONTAINER="${CONTAINER:-}"
CAMERA_TOPIC="${CAMERA_TOPIC:-/camera/color/image_raw}"

if [ -z "$CONTAINER" ]; then
  CONTAINER="$(
    ssh -o BatchMode=yes "$ROBOT_USER@$ROBOT_HOST" \
      "docker ps --format '{{.Names}} {{.Image}}' | awk 'tolower(\$0) ~ /rosmaster|m3pro|yahboom/ {print \$1; exit}'"
  )"
fi

if [ -z "$CONTAINER" ]; then
  echo "No running M3 Pro Docker container found on $ROBOT_HOST" >&2
  exit 1
fi

"$SCRIPT_DIR/stop_showcase_on_robot.sh" >/dev/null 2>&1 || true

ssh -o BatchMode=yes "$ROBOT_USER@$ROBOT_HOST" \
  "docker exec -d \
    -e ROS_DOMAIN_ID=$ROS_DOMAIN_ID \
    -e FASTDDS_BUILTIN_TRANSPORTS=$FASTDDS_BUILTIN_TRANSPORTS \
    -e DISPLAY=:0 \
    $CONTAINER \
    bash -lc 'source /opt/ros/humble/setup.bash
      [ -f /root/yahboomcar_ws/install/setup.bash ] && source /root/yahboomcar_ws/install/setup.bash
      [ -f /root/M3Pro_ws/install/setup.bash ] && source /root/M3Pro_ws/install/setup.bash
      source /root/m3pro_teacher_ws/install/setup.bash
      ros2 launch m3pro_teacher_demos live_showcase.launch.py rviz:=true camera_topic:=$CAMERA_TOPIC >/tmp/m3pro_teacher_live_rviz.log 2>&1'"

sleep 8
ssh -o BatchMode=yes "$ROBOT_USER@$ROBOT_HOST" \
  "docker exec \
    -e ROS_DOMAIN_ID=$ROS_DOMAIN_ID \
    -e FASTDDS_BUILTIN_TRANSPORTS=$FASTDDS_BUILTIN_TRANSPORTS \
    $CONTAINER \
    bash -lc 'source /opt/ros/humble/setup.bash
      [ -f /root/yahboomcar_ws/install/setup.bash ] && source /root/yahboomcar_ws/install/setup.bash
      [ -f /root/M3Pro_ws/install/setup.bash ] && source /root/M3Pro_ws/install/setup.bash
      source /root/m3pro_teacher_ws/install/setup.bash
      echo ---live-processes---
      ps -eo pid=,comm=,args= | grep -E \"live_showcase|sensor_fusion_rgb_demo|arm_joint_state_bridge_demo|robot_state_publisher|rviz2\" | grep -v grep || true
      echo ---live-topics---
      ros2 topic list -t | grep -E \"/scan0|/scan1|/camera/color/image_raw|/camera/depth/points|/teacher/scan_merged|/teacher/fusion_state|/teacher/joint_states|/rgb|/beep\" | sort
      echo ---fusion-sample---
      timeout 8 ros2 topic echo --once /teacher/fusion_state std_msgs/msg/String || true
      echo ---live-log-errors---
      tail -120 /tmp/m3pro_teacher_live_rviz.log | grep -Ei \"error|exception|traceback|process has died|failed\" || true'"

