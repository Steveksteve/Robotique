#!/usr/bin/env bash
#
# Start the full SLAM / Nav2 / explore stack on the M3 Pro in one go.
#
# Usage:
#   ./scripts/start_slam_nav_on_robot.sh [ROBOT_IP] [MODE] [MAP]
#
#   MODE defaults to 'explore'.
#     explore     MAPPING mode — SLAM + Nav2 + explore_lite + rosbridge + camera + web dashboard.
#                 Builds the map autonomously. No pose recovery if the robot is moved.
#     navigation  NAVIGATION mode — AMCL on a SAVED occupancy map + Nav2 + rosbridge + web.
#                 Accepts /initialpose (Set Pose button).
#                 Requires MAP path to the YAML file. Example:
#                   ./scripts/start_slam_nav_on_robot.sh <ip> navigation /root/maps/m3pro_map.yaml
#     localize    NAVIGATION mode via slam_toolbox localization on a SAVED pose graph + Nav2 + rosbridge + web.
#                 Accepts /initialpose (Set Pose button). Requires MAP base path, no extension. Example:
#                   ./scripts/start_slam_nav_on_robot.sh <ip> localize /root/maps/m3pro_map
#     slam-nav    SLAM + Nav2 without explore_lite (manual driving while mapping).
#     nav         [deprecated — use 'navigation'] Alias for AMCL navigation.
#     stop        Stop the whole stack (bringup + SLAM + Nav2 + dashboard).
#     status      Print log tails + running processes.
#
# Env overrides:
#   ROBOT_HOST=192.168.50.104
#   ROBOT_USER=jetson
#   CONTAINER=<name>                (auto-detected if empty)
#   ROS_DOMAIN_ID=30
#   FASTDDS_BUILTIN_TRANSPORTS=UDPv4
#   RVIZ=true|false                 (default false — use Foxglove / dashboard)
#   DASHBOARD=true|false            (default true — HTTP :8080)
#   CAMERA=true|false               (default true — Orbbec RGB+Depth)
#   MICROROS=true|false             (default true — restart the MCU bridge first)
#   OPEN_DASHBOARD=true|false       (default true — `open http://robot:8080` on the Mac)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Positional args with env fallbacks.
ROBOT_HOST="${1:-${ROBOT_HOST:-192.168.50.104}}"
MODE="${2:-explore}"
MAP_ARG="${3:-}"

ROBOT_USER="${ROBOT_USER:-jetson}"
ROS_DOMAIN_ID="${ROS_DOMAIN_ID:-30}"
FASTDDS_BUILTIN_TRANSPORTS="${FASTDDS_BUILTIN_TRANSPORTS:-UDPv4}"
CONTAINER="${CONTAINER:-}"
RVIZ="${RVIZ:-false}"
DASHBOARD="${DASHBOARD:-true}"
CAMERA="${CAMERA:-true}"
MICROROS="${MICROROS:-true}"
OPEN_DASHBOARD="${OPEN_DASHBOARD:-true}"

# Recognize help even when passed as the (positional) robot IP.
case "$ROBOT_HOST" in
  -h|--help)
    sed -n '3,26p' "$0" | sed 's/^# \{0,1\}//'
    exit 0
    ;;
esac

# Auto-detect the M3 Pro container if not provided.
if [ -z "$CONTAINER" ]; then
  CONTAINER="$(
    ssh -o BatchMode=yes "$ROBOT_USER@$ROBOT_HOST" \
      "docker ps --format '{{.Names}} {{.Image}}' | awk 'tolower(\$0) ~ /rosmaster|m3pro|yahboom/ {print \$1; exit}'"
  )"
fi

if [ -z "$CONTAINER" ]; then
  # Not currently RUNNING — try to resurrect the most recently-exited M3 Pro container.
  CONTAINER="$(
    ssh -o BatchMode=yes "$ROBOT_USER@$ROBOT_HOST" \
      "docker ps -a --format '{{.Names}} {{.Image}}' | awk 'tolower(\$0) ~ /rosmaster|m3pro|yahboom/ && tolower(\$0) !~ /micro-ros/ {print \$1; exit}'"
  )"
  if [ -n "$CONTAINER" ]; then
    echo "No running M3 Pro container — resurrecting '$CONTAINER' via docker start..."
    ssh -o BatchMode=yes "$ROBOT_USER@$ROBOT_HOST" "docker start '$CONTAINER'" >/dev/null
    sleep 3
  fi
fi

# Ensure it's actually running (auto-restart if exited).
if ! ssh -o BatchMode=yes "$ROBOT_USER@$ROBOT_HOST" "docker ps --format '{{.Names}}' | grep -qx '$CONTAINER'"; then
  if [ -n "$CONTAINER" ]; then
    echo "Container '$CONTAINER' is stopped — starting it..."
    ssh -o BatchMode=yes "$ROBOT_USER@$ROBOT_HOST" "docker start '$CONTAINER'" >/dev/null || true
    sleep 3
  fi
fi

if [ -z "$CONTAINER" ] || ! ssh -o BatchMode=yes "$ROBOT_USER@$ROBOT_HOST" "docker ps --format '{{.Names}}' | grep -qx '$CONTAINER'"; then
  echo "ERROR: no running M3 Pro container found on $ROBOT_HOST (and docker start failed)" >&2
  exit 1
fi

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

docker_exec_bg() {  # detached; full overlay chain sourced; logs to $1
  local logfile="$1"; shift
  ssh -o BatchMode=yes "$ROBOT_USER@$ROBOT_HOST" \
    "docker exec -d \
       -e ROS_DOMAIN_ID=$ROS_DOMAIN_ID \
       -e FASTDDS_BUILTIN_TRANSPORTS=$FASTDDS_BUILTIN_TRANSPORTS \
       -e DISPLAY=:0 \
       $CONTAINER \
       bash -lc 'set -e
         source /opt/ros/humble/setup.bash
         [ -f /root/yahboomcar_ws/install/setup.bash ] && source /root/yahboomcar_ws/install/setup.bash
         [ -f /root/M3Pro_ws/install/setup.bash ] && source /root/M3Pro_ws/install/setup.bash
         [ -f /root/m3pro_teacher_ws/install/setup.bash ] && source /root/m3pro_teacher_ws/install/setup.bash
         $* >$logfile 2>&1'"
}

proc_running() {
  local pattern="$1"
  ssh -o BatchMode=yes "$ROBOT_USER@$ROBOT_HOST" \
    "docker exec $CONTAINER pgrep -af \"$pattern\" >/dev/null 2>&1"
}

wait_for_topic() {
  local topic="$1"; local timeout_s="${2:-60}"
  printf "  waiting for %s " "$topic"
  local end=$(( $(date +%s) + timeout_s ))
  while [ $(date +%s) -lt $end ]; do
    if ssh -o BatchMode=yes "$ROBOT_USER@$ROBOT_HOST" \
         "docker exec -e ROS_DOMAIN_ID=$ROS_DOMAIN_ID -e FASTDDS_BUILTIN_TRANSPORTS=$FASTDDS_BUILTIN_TRANSPORTS $CONTAINER \
            bash -lc 'source /opt/ros/humble/setup.bash; ros2 topic list 2>/dev/null | grep -qx $topic'" ; then
      echo "OK"; return 0
    fi
    printf "."; sleep 2
  done
  echo "TIMEOUT"; return 1
}

wait_for_port() {
  local port="$1"; local timeout_s="${2:-60}"
  printf "  waiting for :%s " "$port"
  local end=$(( $(date +%s) + timeout_s ))
  while [ $(date +%s) -lt $end ]; do
    if ssh -o BatchMode=yes "$ROBOT_USER@$ROBOT_HOST" \
         "ss -ltn 2>/dev/null | grep -q ':$port '" ; then
      echo "OK"; return 0
    fi
    printf "."; sleep 2
  done
  echo "TIMEOUT"; return 1
}

stop_stack() {
  # IMPORTANT: only target the *launch files we ourselves started*, by name.
  # Using broad `pkill -f <node>` on this image cascades into the container's
  # PID-1 descendants and will kill the container (observed: `Exited (0)`).
  echo "Stopping the stack on $CONTAINER ..."
  ssh -o BatchMode=yes "$ROBOT_USER@$ROBOT_HOST" \
    "docker exec $CONTAINER bash -lc \"
      for pat in \
        'base_bringup.launch.py' \
        'slam_and_nav.launch.py' \
        'explore.launch.py' \
        'navigation.launch.py' \
        'web_dashboard.launch.py' \
        'app_camera.launch.py'; do
        for pid in \\\$(ps -eo pid=,args= | awk -v p=\\\"\$pat\\\" 'index(\\\$0,p){print \\\$1}'); do
          # SIGINT first for graceful shutdown; ros2 launch propagates to children.
          kill -INT \\\$pid 2>/dev/null || true
        done
      done
      sleep 3
      # Safety: publish zero twist so the base doesn't coast.
      source /opt/ros/humble/setup.bash 2>/dev/null || true
      timeout 2 ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist '{linear: {x: 0.0}, angular: {z: 0.0}}' >/dev/null 2>&1 || true
    \""
  echo "Done."
}

status_stack() {
  ssh -o BatchMode=yes "$ROBOT_USER@$ROBOT_HOST" \
    "docker exec $CONTAINER bash -lc \"
      for f in /tmp/m3pro_bringup.log /tmp/m3pro_camera.log /tmp/m3pro_slam_nav.log /tmp/m3pro_explore.log /tmp/m3pro_nav.log /tmp/m3pro_dashboard.log; do
        if [ -f \\\$f ]; then echo \\\"--- \\\$f (last 15) ---\\\"; tail -n 15 \\\$f; echo; fi
      done
      echo '--- running processes ---'
      ps -eo pid=,args= | grep -E 'ros2 launch|rviz2|slam_toolbox|controller_server|planner_server|explore_node|rosbridge|web_server_node|ekf_node|base_bringup|app_camera' | grep -v grep || true
      echo
      echo '--- load ---'
      uptime
    \""
}

# ---------------------------------------------------------------------------
# Mode dispatch
# ---------------------------------------------------------------------------

case "$MODE" in
  stop)   stop_stack; exit 0 ;;
  status) status_stack; exit 0 ;;
  slam-nav|explore|nav|navigation|localize) ;;
  *)
    echo "ERROR: unknown mode '$MODE'" >&2
    sed -n '3,26p' "$0" | sed 's/^# \{0,1\}//'
    exit 1
    ;;
esac

if [[ "$MODE" == "nav" || "$MODE" == "navigation" ]]; then
  if [[ -z "$MAP_ARG" ]]; then
    echo "ERROR: '$MODE' mode needs a map path as 3rd arg." >&2
    echo "  - '$MODE' uses AMCL and wants a map yaml path. Example:" >&2
    echo "      $0 $ROBOT_HOST navigation /root/maps/m3pro_map.yaml" >&2
    exit 1
  fi
fi

if [[ "$MODE" == "localize" ]]; then
  if [[ -z "$MAP_ARG" ]]; then
    echo "ERROR: '$MODE' mode needs a map base path as 3rd arg." >&2
    echo "  - 'localize' uses slam_toolbox localization and wants the base name" >&2
    echo "    (without .data/.posegraph). Example:" >&2
    echo "      $0 $ROBOT_HOST localize /root/maps/m3pro_map" >&2
    exit 1
  fi
fi

echo "╭─ M3 Pro SLAM stack ─────────────────────────────────────────────────"
echo "│ Robot      : $ROBOT_USER@$ROBOT_HOST"
echo "│ Container  : $CONTAINER"
echo "│ Mode       : $MODE${MAP_ARG:+ ($MAP_ARG)}"
echo "│ Domain     : $ROS_DOMAIN_ID / $FASTDDS_BUILTIN_TRANSPORTS"
echo "│ rviz=$RVIZ dashboard=$DASHBOARD camera=$CAMERA microros=$MICROROS"
echo "╰─────────────────────────────────────────────────────────────────────"
echo

# Clean slate first — avoids the duplicate-bringup CPU hazard. Skippable on
# images where any SIGINT inside the container cascades into PID 1 (some
# xterm-based init scripts exit on child SIGINT → container dies).
# NOTE: the default Yahboom image's PID-1 is an xterm-wrapped start.py.
# SIGINT inside the container can cascade and exit the xterm → container dies.
# Opt-in only: set NO_STOP_FIRST=false to risk it.
if [[ "${NO_STOP_FIRST:-true}" != "true" ]]; then
  stop_stack >/dev/null 2>&1 || true
  sleep 1
fi

# ---------------------------------------------------------------------------
# 1) micro-ros-agent (MCU <-> DDS)
# ---------------------------------------------------------------------------
if [[ "$MICROROS" == "true" ]]; then
  echo "▶ [1/5] micro-ros-agent"
  ROBOT_HOST="$ROBOT_HOST" "$SCRIPT_DIR/restart_microros_agent.sh" 2>&1 | tail -5 | sed 's/^/  /' || true
else
  echo "▶ [1/5] micro-ros-agent SKIPPED"
fi
echo

# ---------------------------------------------------------------------------
# 2) Yahboom bringup — lidars, IMU, EKF, robot_state_publisher, laserscan merger
# ---------------------------------------------------------------------------
echo "▶ [2/5] Yahboom base_bringup"
docker_exec_bg /tmp/m3pro_bringup.log \
  "ros2 launch M3Pro_navigation base_bringup.launch.py"
wait_for_topic /scan_multi 60 || { echo "bringup failed — tail /tmp/m3pro_bringup.log"; exit 2; }
echo

# ---------------------------------------------------------------------------
# 3) Camera
# ---------------------------------------------------------------------------
if [[ "$CAMERA" == "true" ]]; then
  echo "▶ [3/5] Orbbec camera"
  docker_exec_bg /tmp/m3pro_camera.log \
    "ros2 launch slam_mapping app_camera.launch.py"
  echo "  launched (log: /tmp/m3pro_camera.log)"
else
  echo "▶ [3/5] camera SKIPPED"
fi
echo

# ---------------------------------------------------------------------------
# 4) SLAM / Nav2 / explore according to MODE
# ---------------------------------------------------------------------------
STACK_LOG=""
case "$MODE" in
  slam-nav)
    echo "▶ [4/5] SLAM + Nav2 (slam_and_nav.launch.py)"
    docker_exec_bg /tmp/m3pro_slam_nav.log \
      "ros2 launch m3pro_teacher_nav slam_and_nav.launch.py rviz:=$RVIZ"
    STACK_LOG=/tmp/m3pro_slam_nav.log
    ;;
  explore)
    echo "▶ [4/5] MAPPING mode — explore.launch.py (SLAM + Nav2 + explore_lite + rosbridge :9090)"
    docker_exec_bg /tmp/m3pro_explore.log \
      "ros2 launch m3pro_teacher_nav explore.launch.py"
    STACK_LOG=/tmp/m3pro_explore.log
    wait_for_port 9090 60 || { echo "explore stack failed — tail $STACK_LOG"; exit 3; }
    ;;
  navigation|nav)
    echo "▶ [4/5] NAVIGATION mode — navigation.launch.py (AMCL) on saved map ($MAP_ARG)"
    docker_exec_bg /tmp/m3pro_nav.log \
      "ros2 launch m3pro_teacher_nav navigation.launch.py map:=$MAP_ARG rviz:=$RVIZ rosbridge:=true"
    STACK_LOG=/tmp/m3pro_nav.log
    wait_for_port 9090 60 || { echo "navigation stack failed — tail $STACK_LOG"; exit 3; }
    ;;
  localize)
    echo "▶ [4/5] NAVIGATION mode — localize.launch.py on saved pose graph ($MAP_ARG)"
    docker_exec_bg /tmp/m3pro_localize.log \
      "ros2 launch m3pro_teacher_nav localize.launch.py map:=$MAP_ARG"
    STACK_LOG=/tmp/m3pro_localize.log
    wait_for_port 9090 60 || { echo "localize stack failed — tail $STACK_LOG"; exit 3; }
    ;;
esac
wait_for_topic /map 60 || { echo "WARN: /map not yet published — continuing (SLAM may still be initializing)"; }
echo

# ---------------------------------------------------------------------------
# 5) Web dashboard (HTTP :8080)
# ---------------------------------------------------------------------------
if [[ "$DASHBOARD" == "true" ]]; then
  echo "▶ [5/5] web_dashboard.launch.py"
  # Some mode launches already provide rosbridge on :9090.
  local_rosbridge="true"
  case "$MODE" in
    explore|navigation|nav|localize) local_rosbridge="false" ;;
  esac
  docker_exec_bg /tmp/m3pro_dashboard.log \
    "ros2 launch m3pro_teacher_web web_dashboard.launch.py rosbridge:=$local_rosbridge port:=8080"
  wait_for_port 8080 30 || { echo "dashboard failed to open — tail /tmp/m3pro_dashboard.log"; }
  wait_for_port 9090 30 || true
else
  echo "▶ [5/5] dashboard SKIPPED"
fi
echo

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
cat <<EOF
╭─ STACK '$MODE' UP ─────────────────────────────────────────────────────
EOF
[[ "$DASHBOARD" == "true" ]] && cat <<EOF
│ Dashboard : http://$ROBOT_HOST:8080
EOF
cat <<EOF
│ rosbridge : ws://$ROBOT_HOST:9090     (Foxglove → Rosbridge)
│ VNC       : vnc://$ROBOT_HOST:5900
│
│ Mic / push-to-talk needs 'secure context'. Over LAN HTTP the browser
│ only allows it on localhost. On the Mac:
│
│   ssh -fN -L 8080:localhost:8080 -L 9090:localhost:9090 $ROBOT_USER@$ROBOT_HOST
│   open http://localhost:8080
│
│ Logs (on the robot):
│   ssh $ROBOT_USER@$ROBOT_HOST "docker exec $CONTAINER tail -f /tmp/m3pro_bringup.log"
│   ssh $ROBOT_USER@$ROBOT_HOST "docker exec $CONTAINER tail -f $STACK_LOG"
│
│ Status :  $0 $ROBOT_HOST status
│ Stop   :  $0 $ROBOT_HOST stop
╰─────────────────────────────────────────────────────────────────────
EOF

if [[ "$DASHBOARD" == "true" && "$OPEN_DASHBOARD" == "true" ]] && command -v open >/dev/null 2>&1; then
  open "http://$ROBOT_HOST:8080" >/dev/null 2>&1 || true
fi
