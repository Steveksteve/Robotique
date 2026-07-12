#!/usr/bin/env python3
"""
Autonomous frontier exploration — the robot maps the room like a Roomba.

Algorithm:
  1. Subscribe to /map (OccupancyGrid from slam_toolbox)
  2. Find frontier cells: free cells (0) adjacent to unknown cells (-1)
  3. Cluster nearby frontier cells into groups
  4. Pick the nearest reachable frontier cluster
  5. Send a Nav2 goal to its centroid
  6. Wait until the robot arrives (or gets stuck), then repeat
  7. Stop when no more frontiers exist (map is complete)

Usage:
  # First launch SLAM + Nav2:
  ros2 launch m3pro_teacher_nav slam_and_nav.launch.py

  # Then start exploration:
  ros2 run m3pro_teacher_demos frontier_explorer_demo
"""
import math
from collections import deque
from typing import List, Optional, Tuple

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
from nav_msgs.msg import OccupancyGrid, Odometry


class FrontierExplorerDemo(Node):

    # Map cell values
    FREE = 0
    UNKNOWN = -1

    def __init__(self):
        super().__init__("frontier_explorer_demo")

        self.min_frontier_size = int(
            self.declare_parameter("min_frontier_size", 8).value
        )
        self.goal_tolerance = float(
            self.declare_parameter("goal_tolerance", 0.4).value
        )
        self.stuck_timeout = float(
            self.declare_parameter("stuck_timeout", 20.0).value
        )
        self.replan_interval = float(
            self.declare_parameter("replan_interval", 5.0).value
        )

        self.map_data: Optional[OccupancyGrid] = None
        self.robot_x = 0.0
        self.robot_y = 0.0
        self.current_goal: Optional[Tuple[float, float]] = None
        self.last_progress_time = self.get_clock().now()
        self.last_x = 0.0
        self.last_y = 0.0
        self.goals_sent = 0
        self.finished = False

        self.create_subscription(OccupancyGrid, "/map", self.on_map, 1)
        self.create_subscription(Odometry, "/odom", self.on_odom, 5)
        self.goal_pub = self.create_publisher(PoseStamped, "/goal_pose", 10)

        self.create_timer(self.replan_interval, self.explore_tick)
        self.get_logger().info(
            "Frontier explorer started — waiting for map and odometry..."
        )

    def on_map(self, msg: OccupancyGrid):
        self.map_data = msg

    def on_odom(self, msg: Odometry):
        self.robot_x = msg.pose.pose.position.x
        self.robot_y = msg.pose.pose.position.y

    def explore_tick(self):
        if self.finished or self.map_data is None:
            return

        # Check if we arrived at the current goal
        if self.current_goal is not None:
            dx = self.robot_x - self.current_goal[0]
            dy = self.robot_y - self.current_goal[1]
            if math.hypot(dx, dy) < self.goal_tolerance:
                self.get_logger().info("Reached goal, looking for next frontier...")
                self.current_goal = None

        # Check if robot is stuck (hasn't moved much)
        if self.current_goal is not None:
            moved = math.hypot(
                self.robot_x - self.last_x, self.robot_y - self.last_y
            )
            elapsed = (
                self.get_clock().now() - self.last_progress_time
            ).nanoseconds / 1e9

            if moved > 0.1:
                self.last_progress_time = self.get_clock().now()
                self.last_x = self.robot_x
                self.last_y = self.robot_y
            elif elapsed > self.stuck_timeout:
                self.get_logger().warning(
                    "Robot seems stuck, picking a different frontier..."
                )
                self.current_goal = None

        # Find and go to next frontier
        if self.current_goal is None:
            self.find_and_go_to_frontier()

    def find_and_go_to_frontier(self):
        grid = self.map_data
        w = grid.info.width
        h = grid.info.height
        res = grid.info.resolution
        ox = grid.info.origin.position.x
        oy = grid.info.origin.position.y
        data = list(grid.data)

        # Find all frontier cells (free cells next to unknown cells)
        frontier_cells: List[Tuple[int, int]] = []
        for y in range(1, h - 1):
            for x in range(1, w - 1):
                idx = y * w + x
                if data[idx] != self.FREE:
                    continue
                # Check 4-connected neighbors for unknown
                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    ni = (y + dy) * w + (x + dx)
                    if data[ni] == self.UNKNOWN:
                        frontier_cells.append((x, y))
                        break

        if not frontier_cells:
            if not self.finished:
                self.get_logger().info(
                    f"No more frontiers! Map is complete. "
                    f"Sent {self.goals_sent} goals total."
                )
                self.finished = True
            return

        # Cluster frontier cells using flood-fill (BFS)
        visited = set()
        clusters: List[List[Tuple[int, int]]] = []
        for cell in frontier_cells:
            if cell in visited:
                continue
            cluster = []
            queue = deque([cell])
            visited.add(cell)
            while queue:
                cx, cy = queue.popleft()
                cluster.append((cx, cy))
                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1),
                               (-1, -1), (1, -1), (-1, 1), (1, 1)]:
                    nb = (cx + dx, cy + dy)
                    if nb in visited:
                        continue
                    if nb in frontier_cells or (
                        nb[0], nb[1]
                    ) in set(frontier_cells):
                        # Quick membership check — use set for large maps
                        pass
                    # Simpler: check if neighbor is also a frontier cell
                    nx, ny = nb
                    if 0 <= nx < w and 0 <= ny < h:
                        ni = ny * w + nx
                        if data[ni] == self.FREE:
                            has_unknown = False
                            for ddx, ddy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                                nni = (ny + ddy) * w + (nx + ddx)
                                if 0 <= nni < len(data) and data[nni] == self.UNKNOWN:
                                    has_unknown = True
                                    break
                            if has_unknown and nb not in visited:
                                visited.add(nb)
                                queue.append(nb)
            if len(cluster) >= self.min_frontier_size:
                clusters.append(cluster)

        if not clusters:
            if not self.finished:
                self.get_logger().info(
                    f"All frontiers too small (< {self.min_frontier_size} cells). "
                    f"Map is likely complete. Sent {self.goals_sent} goals total."
                )
                self.finished = True
            return

        # Compute centroid of each cluster in map coordinates
        centroids: List[Tuple[float, float, int]] = []
        for cluster in clusters:
            cx = sum(p[0] for p in cluster) / len(cluster) * res + ox
            cy = sum(p[1] for p in cluster) / len(cluster) * res + oy
            centroids.append((cx, cy, len(cluster)))

        # Pick the nearest frontier (balancing distance and size)
        best = None
        best_score = float("inf")
        for cx, cy, size in centroids:
            dist = math.hypot(cx - self.robot_x, cy - self.robot_y)
            # Prefer closer frontiers but give bonus to larger ones
            score = dist - 0.02 * size
            if score < best_score:
                best_score = score
                best = (cx, cy, size)

        if best is None:
            return

        gx, gy, size = best
        self.send_goal(gx, gy)
        self.current_goal = (gx, gy)
        self.last_progress_time = self.get_clock().now()
        self.last_x = self.robot_x
        self.last_y = self.robot_y
        self.goals_sent += 1
        self.get_logger().info(
            f"Goal #{self.goals_sent}: frontier at ({gx:.2f}, {gy:.2f}), "
            f"size={size} cells, {len(clusters)} frontiers remaining"
        )

    def send_goal(self, x: float, y: float):
        msg = PoseStamped()
        msg.header.frame_id = "map"
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.pose.position.x = x
        msg.pose.position.y = y
        msg.pose.orientation.w = 1.0
        self.goal_pub.publish(msg)


def main():
    rclpy.init()
    node = FrontierExplorerDemo()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        try:
            node.destroy_node()
        except KeyboardInterrupt:
            pass
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
