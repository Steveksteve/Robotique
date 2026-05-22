#!/usr/bin/env python3
"""
Keyboard teleoperation for the Yahboom M3 Pro 6-servo arm.

Run this script in a terminal that has ROS 2 and the Yahboom arm messages
sourced. It publishes arm_msgs/ArmJoints commands while keeping every servo
inside the safe 0..180 degree range.
"""

import argparse
import select
import sys
import termios
import tty
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

try:
    import rclpy
    from rclpy.node import Node
except ImportError:
    rclpy = None
    Node = object

try:
    from arm_msgs.msg import ArmJoints
except ImportError:
    ArmJoints = None


HOME = [90, 120, 10, 20, 90, 30]
CENTER = [90, 90, 90, 90, 90, 30]
JOINT_LABELS = [
    "j1 base_yaw",
    "j2 shoulder",
    "j3 elbow",
    "j4 wrist_pitch",
    "j5 wrist_roll",
    "j6 gripper",
]


KEYMAP: Dict[str, Tuple[int, int]] = {
    "a": (0, -1),
    "d": (0, 1),
    "w": (1, 1),
    "s": (1, -1),
    "e": (2, 1),
    "r": (2, -1),
    "i": (3, 1),
    "k": (3, -1),
    "j": (4, -1),
    "l": (4, 1),
    "o": (5, -1),
    "p": (5, 1),
}


HELP_TEXT = """
Controle clavier du bras Yahboom M3 Pro

Touches:
  a / d    base gauche / droite
  w / s    epaule haut / bas
  e / r    coude + / -
  i / k    poignet haut / bas
  j / l    rotation pince gauche / droite
  o / p    pince ouvrir / fermer

  h        position home [90,120,10,20,90,30]
  x        position centre [90,90,90,90,90,30]
  + / -    augmenter / reduire le pas clavier
  espace   republier la pose courante
  ?        afficher cette aide
  q        quitter
"""


def clamp(value: int, low: int = 0, high: int = 180) -> int:
    return max(low, min(high, int(value)))


def format_pose(pose: List[int]) -> str:
    parts = [f"j{i + 1}={v:3d}" for i, v in enumerate(pose)]
    return "[" + " ".join(parts) + "]"


def read_key(timeout: float = 0.1) -> Optional[str]:
    readable, _, _ = select.select([sys.stdin], [], [], timeout)
    if not readable:
        return None
    return sys.stdin.read(1)


@dataclass
class ArmKeyboardConfig:
    topic: str
    step: int
    servo_time_ms: int
    publish_on_start: bool
    dry_run: bool


class ArmKeyboardNode(Node):
    def __init__(self, config: ArmKeyboardConfig):
        super().__init__("control_bras_clavier")
        self.config = config
        self.pose = HOME[:]
        self.step = config.step
        self.pub = None

        if not config.dry_run and ArmJoints is not None:
            self.pub = self.create_publisher(ArmJoints, config.topic, 10)
            self.get_logger().info(f"Publication ArmJoints sur {config.topic}")
        else:
            reason = "option --dry-run" if config.dry_run else "arm_msgs indisponible"
            self.get_logger().warning(f"Mode dry-run actif ({reason})")

        if config.publish_on_start:
            self.publish_pose("home initial")

    def publish_pose(self, reason: str) -> None:
        self.pose = [clamp(v) for v in self.pose]
        if self.pub is not None:
            msg = ArmJoints()
            msg.joint1 = self.pose[0]
            msg.joint2 = self.pose[1]
            msg.joint3 = self.pose[2]
            msg.joint4 = self.pose[3]
            msg.joint5 = self.pose[4]
            msg.joint6 = self.pose[5]
            if hasattr(msg, "time"):
                msg.time = int(self.config.servo_time_ms)
            self.pub.publish(msg)
        self.get_logger().info(f"{reason}: {format_pose(self.pose)} step={self.step}")

    def apply_key(self, key: str) -> bool:
        if key in KEYMAP:
            joint_index, direction = KEYMAP[key]
            self.pose[joint_index] = clamp(self.pose[joint_index] + direction * self.step)
            self.publish_pose(JOINT_LABELS[joint_index])
            return True

        if key == "h":
            self.pose = HOME[:]
            self.publish_pose("home")
            return True

        if key == "x":
            self.pose = CENTER[:]
            self.publish_pose("centre")
            return True

        if key == " ":
            self.publish_pose("republish")
            return True

        if key == "+":
            self.step = clamp(self.step + 1, 1, 30)
            self.get_logger().info(f"step={self.step}")
            return True

        if key == "-":
            self.step = clamp(self.step - 1, 1, 30)
            self.get_logger().info(f"step={self.step}")
            return True

        if key == "?":
            print(HELP_TEXT)
            return True

        return False


def parse_args() -> ArmKeyboardConfig:
    parser = argparse.ArgumentParser(
        description="Controle clavier du bras Yahboom M3 Pro via arm_msgs/ArmJoints."
    )
    parser.add_argument(
        "--topic",
        default="/arm_control",
        help="Topic de commande du bras. Essayez /arm6_joints si votre firmware commande directement ce topic.",
    )
    parser.add_argument("--step", type=int, default=5, help="Pas en degres par touche.")
    parser.add_argument(
        "--servo-time-ms",
        type=int,
        default=700,
        help="Duree de mouvement servo envoyee dans le champ time si disponible.",
    )
    parser.add_argument(
        "--no-start-publish",
        action="store_true",
        help="Ne pas envoyer la pose home au demarrage.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Afficher les commandes sans publier sur le bras.",
    )
    args = parser.parse_args()

    return ArmKeyboardConfig(
        topic=args.topic,
        step=clamp(args.step, 1, 30),
        servo_time_ms=max(100, int(args.servo_time_ms)),
        publish_on_start=not args.no_start_publish,
        dry_run=bool(args.dry_run),
    )


def main() -> int:
    config = parse_args()
    if rclpy is None:
        print("Erreur: rclpy est indisponible. Sourcez ROS 2 avant de lancer ce script.", file=sys.stderr)
        return 2

    rclpy.init()
    node = ArmKeyboardNode(config)
    old_settings = termios.tcgetattr(sys.stdin)

    print(HELP_TEXT)
    print(f"Topic: {config.topic} | pose: {format_pose(node.pose)}")

    try:
        tty.setcbreak(sys.stdin.fileno())
        while rclpy.ok():
            rclpy.spin_once(node, timeout_sec=0.0)
            key = read_key(0.1)
            if key is None:
                continue
            if key == "q":
                node.publish_pose("sortie")
                break
            if key == "\x03":
                break
            if not node.apply_key(key):
                node.get_logger().info("Touche inconnue. Appuyez sur ? pour l'aide.")
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
