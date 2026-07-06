#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  ./scripts/deploy_workspace_to_robot.sh ROBOT_IP [WORKSPACE_DIR]

Examples:
  ./scripts/deploy_workspace_to_robot.sh 192.168.50.102
  ./scripts/deploy_workspace_to_robot.sh 192.168.50.103 ~/m3pro_teacher_ws

Environment overrides:
  ROBOT_USER=jetson
  REMOTE_WS_NAME=m3pro_teacher_ws
  CONTAINER=vibrant_lehmann
  ROS_DOMAIN_ID=30
  FASTDDS_BUILTIN_TRANSPORTS=UDPv4
  BUILD=1

What it does:
  1. rsyncs this workspace to ~/m3pro_teacher_ws on the Jetson host.
  2. If BUILD=1, finds the running Yahboom/M3Pro Docker container.
  3. If BUILD=1, copies the workspace into /root/m3pro_teacher_ws in Docker.
  4. If BUILD=1, runs colcon build --symlink-install inside Docker.
EOF
}

if [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ] || [ "$#" -lt 1 ] || [ "$#" -gt 2 ]; then
  usage
  exit 1
fi

ROBOT_HOST="$1"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${2:-$SCRIPT_DIR/..}" && pwd)"

ROBOT_USER="${ROBOT_USER:-jetson}"
REMOTE_WS_NAME="${REMOTE_WS_NAME:-$(basename "$ROOT_DIR")}"
CONTAINER="${CONTAINER:-}"
ROS_DOMAIN_ID="${ROS_DOMAIN_ID:-30}"
FASTDDS_BUILTIN_TRANSPORTS="${FASTDDS_BUILTIN_TRANSPORTS:-UDPv4}"
BUILD="${BUILD:-1}"

HOST_WS="/home/$ROBOT_USER/$REMOTE_WS_NAME"
CONTAINER_WS="/root/$REMOTE_WS_NAME"

echo "Robot:          $ROBOT_USER@$ROBOT_HOST"
echo "Local workspace: $ROOT_DIR"
echo "Host workspace:  $HOST_WS"
echo "Docker workspace:$CONTAINER_WS"

echo
echo "Checking SSH..."
ssh -o BatchMode=yes -o ConnectTimeout=5 "$ROBOT_USER@$ROBOT_HOST" "hostname && whoami"

echo
echo "Copying workspace to Jetson host..."
rsync -az --delete \
  --exclude '.git' \
  --exclude '.DS_Store' \
  --exclude '__pycache__' \
  --exclude 'build' \
  --exclude 'install' \
  --exclude 'log' \
  "$ROOT_DIR/" "$ROBOT_USER@$ROBOT_HOST:$REMOTE_WS_NAME/"

if [ "$BUILD" = "0" ]; then
  echo
  echo "BUILD=0, stopping after host rsync."
  echo "Workspace copied to $ROBOT_USER@$ROBOT_HOST:$HOST_WS"
  echo "Docker workspace was not modified."
  exit 0
fi

if [ -z "$CONTAINER" ]; then
  CONTAINER="$(
    ssh -o BatchMode=yes "$ROBOT_USER@$ROBOT_HOST" \
      "docker ps --format '{{.Names}} {{.Image}}' | awk 'tolower(\$0) ~ /rosmaster|m3pro|yahboom/ {print \$1; exit}'"
  )"
fi

if [ -z "$CONTAINER" ]; then
  echo "No running Yahboom/M3Pro Docker container found on $ROBOT_HOST." >&2
  echo "Check with:" >&2
  echo "  ssh $ROBOT_USER@$ROBOT_HOST 'docker ps --format \"{{.Names}}  {{.Image}}\"'" >&2
  exit 2
fi

echo
echo "Using Docker container: $CONTAINER"
echo "Copying workspace into Docker..."
ssh -o BatchMode=yes "$ROBOT_USER@$ROBOT_HOST" \
  "docker exec $CONTAINER rm -rf '$CONTAINER_WS' && docker cp '$HOST_WS' $CONTAINER:'$CONTAINER_WS'"

echo
echo "Building workspace in Docker..."
ssh -o BatchMode=yes "$ROBOT_USER@$ROBOT_HOST" \
  "docker exec \
    -e ROS_DOMAIN_ID='$ROS_DOMAIN_ID' \
    -e FASTDDS_BUILTIN_TRANSPORTS='$FASTDDS_BUILTIN_TRANSPORTS' \
    $CONTAINER \
    bash -lc 'set -e
      source /opt/ros/humble/setup.bash
      [ -f /root/yahboomcar_ws/install/setup.bash ] && source /root/yahboomcar_ws/install/setup.bash
      [ -f /root/M3Pro_ws/install/setup.bash ] && source /root/M3Pro_ws/install/setup.bash
      cd $CONTAINER_WS
      colcon build --symlink-install'"

echo
echo "Deploy complete."
echo
echo "Open a ROS shell manually with:"
echo "  ssh $ROBOT_USER@$ROBOT_HOST"
echo "  docker exec -it -e ROS_DOMAIN_ID=$ROS_DOMAIN_ID -e FASTDDS_BUILTIN_TRANSPORTS=$FASTDDS_BUILTIN_TRANSPORTS -e DISPLAY=:0 $CONTAINER bash"
echo "  source /opt/ros/humble/setup.bash"
echo "  source /root/yahboomcar_ws/install/setup.bash 2>/dev/null || true"
echo "  source /root/M3Pro_ws/install/setup.bash 2>/dev/null || true"
echo "  source $CONTAINER_WS/install/setup.bash"
