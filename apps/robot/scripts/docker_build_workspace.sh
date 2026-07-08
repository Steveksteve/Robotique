#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
IMAGE="${IMAGE:-m3pro_teacher_ws:humble}"

cd "$ROOT_DIR"

docker build -t "$IMAGE" .

docker run --rm \
  -e ROS_DOMAIN_ID="${ROS_DOMAIN_ID:-30}" \
  -e FASTDDS_BUILTIN_TRANSPORTS="${FASTDDS_BUILTIN_TRANSPORTS:-UDPv4}" \
  "$IMAGE" \
  bash -lc "source /opt/ros/humble/setup.bash && source /root/m3pro_teacher_ws/install/setup.bash && ros2 pkg list | grep m3pro_teacher"
