import { useState } from "react";
import type { Mission, Position } from "../types/mission";

export function useWebSocket() {
  const [robotStatus] = useState("idle");

  const [position] = useState<Position>({
    x: 120,
    y: 150,
  });

  const [missions] = useState<Mission[]>([
    { id: 1, from: "A", to: "B", status: "created" },
    { id: 2, from: "Stock", to: "Desk", status: "navigating" },
  ]);

  const [trail] = useState<Position[]>([
    { x: 100, y: 130 },
    { x: 110, y: 140 },
    { x: 120, y: 150 },
  ]);

  return { robotStatus, position, missions, trail };
}