#!/usr/bin/env bash
set -euo pipefail

ROBOT_HOST="${ROBOT_HOST:-192.168.50.102}"
ROBOT_USER="${ROBOT_USER:-jetson}"
ROS_DOMAIN_ID="${ROS_DOMAIN_ID:-30}"
FASTDDS_BUILTIN_TRANSPORTS="${FASTDDS_BUILTIN_TRANSPORTS:-UDPv4}"
CONTAINER="${CONTAINER:-}"

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

ssh -o BatchMode=yes "$ROBOT_USER@$ROBOT_HOST" \
  "docker exec -d \
    -e ROS_DOMAIN_ID=$ROS_DOMAIN_ID \
    -e FASTDDS_BUILTIN_TRANSPORTS=$FASTDDS_BUILTIN_TRANSPORTS \
    -e DISPLAY=:0 \
    $CONTAINER \
    bash -lc 'source /opt/ros/humble/setup.bash
      [ -f /root/yahboomcar_ws/install/setup.bash ] && source /root/yahboomcar_ws/install/setup.bash
      [ -f /root/M3Pro_ws/install/setup.bash ] && source /root/M3Pro_ws/install/setup.bash
      ros2 launch slam_mapping app_camera.launch.py >/tmp/m3pro_camera.log 2>&1'"

sleep 8
ssh -o BatchMode=yes "$ROBOT_USER@$ROBOT_HOST" \
  "docker exec \
    -e ROS_DOMAIN_ID=$ROS_DOMAIN_ID \
    -e FASTDDS_BUILTIN_TRANSPORTS=$FASTDDS_BUILTIN_TRANSPORTS \
    $CONTAINER \
    bash -lc 'source /opt/ros/humble/setup.bash
      [ -f /root/yahboomcar_ws/install/setup.bash ] && source /root/yahboomcar_ws/install/setup.bash
      [ -f /root/M3Pro_ws/install/setup.bash ] && source /root/M3Pro_ws/install/setup.bash
      ros2 topic list -t | grep -Ei \"camera|image|depth|points|rgb|color\" | sort
      echo ---camera-log---
      tail -80 /tmp/m3pro_camera.log 2>/dev/null | grep -Ei \"Device|stream|error|failed|connected|process\" || true'"

