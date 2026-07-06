#!/usr/bin/env bash
set -euo pipefail

ROBOT_HOST="${ROBOT_HOST:-192.168.50.102}"
ROBOT_USER="${ROBOT_USER:-jetson}"
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
  "docker exec $CONTAINER bash -lc \"for pid in \\\$(ps -eo pid=,comm=,args= | awk '\\\$2 == \\\"ros2\\\" && /ros2 launch m3pro_teacher_demos/ {print \\\$1}'); do kill -INT \\\$pid 2>/dev/null || true; done; sleep 2; for pid in \\\$(ps -eo pid=,comm=,args= | awk '\\\$2 == \\\"ros2\\\" && /ros2 launch m3pro_teacher_demos/ {print \\\$1}'); do kill -TERM \\\$pid 2>/dev/null || true; done; pkill -TERM -x rviz2 2>/dev/null || true\""
