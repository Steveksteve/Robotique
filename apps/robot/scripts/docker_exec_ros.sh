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

if [ "$#" -gt 0 ]; then
  REMOTE_CMD="$*"
else
  REMOTE_CMD="exec bash"
fi

ssh -t "$ROBOT_USER@$ROBOT_HOST" \
  "docker exec -it \
    -e ROS_DOMAIN_ID=$ROS_DOMAIN_ID \
    -e FASTDDS_BUILTIN_TRANSPORTS=$FASTDDS_BUILTIN_TRANSPORTS \
    -e DISPLAY=:0 \
    $CONTAINER \
    bash -lc 'set -e
      source /opt/ros/humble/setup.bash
      [ -f /root/yahboomcar_ws/install/setup.bash ] && source /root/yahboomcar_ws/install/setup.bash
      [ -f /root/M3Pro_ws/install/setup.bash ] && source /root/M3Pro_ws/install/setup.bash
      [ -f /root/m3pro_teacher_ws/install/setup.bash ] && source /root/m3pro_teacher_ws/install/setup.bash
      cd /root/m3pro_teacher_ws 2>/dev/null || cd /root
      $REMOTE_CMD'"

