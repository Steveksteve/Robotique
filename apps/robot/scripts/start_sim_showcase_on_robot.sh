#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
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
      ros2 launch m3pro_teacher_demos sim_showcase.launch.py rviz:=true >/tmp/m3pro_teacher_rviz.log 2>&1'"

sleep 3
ssh -o BatchMode=yes "$ROBOT_USER@$ROBOT_HOST" \
  "docker exec $CONTAINER bash -lc \"ps -eo pid=,comm=,args= | awk '\\\$2 == \\\"python3\\\" && /ros2 launch m3pro_teacher_demos sim_showcase.launch.py/ {print}' || true; pgrep -a rviz2 || true; tail -40 /tmp/m3pro_teacher_rviz.log 2>/dev/null || true\""

