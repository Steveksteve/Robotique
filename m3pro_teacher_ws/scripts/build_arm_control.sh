#!/bin/bash
# Clean build script for the arm control packages on Jetson.

set -e

echo "[arm] Cleaning build directories..."
cd /root/m3pro_teacher_ws
rm -rf build install log

echo "[arm] Building interfaces and control node..."
colcon build --symlink-install --packages-select m3pro_teacher_interfaces m3pro_teacher_demos

echo "[arm] Sourcing setup..."
source install/setup.bash

echo "[arm] Build complete."
echo
echo "[arm] Service check:"
ros2 service list | grep arm || echo "[arm] No arm services yet. Start the node first."

echo
echo "[arm] Launch the manual control node with:"
echo "  ros2 run m3pro_teacher_demos arm_manual_control_node"
