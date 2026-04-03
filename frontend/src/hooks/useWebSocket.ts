import { useEffect, useState } from "react";

type Mission = {
  id: string;
  from: string;
  to: string;
  status: "idle" | "navigating" | "completed";
};

export const useWebSocket = () => {
  const [robotStatus, setRobotStatus] = useState("idle");
  const [position, setPosition] = useState({ x: 20, y: 20 });
  const [trail, setTrail] = useState<{ x: number; y: number }[]>([]);

  const [missions, setMissions] = useState<Mission[]>([
    { id: "1", from: "Dock", to: "Zone A", status: "navigating" },
    { id: "2", from: "Zone A", to: "Dock", status: "idle" },
  ]);

  useEffect(() => {
    const interval = setInterval(() => {
      // mouvement robot
      setPosition((p) => {
        const newPos = {
          x: (p.x + Math.random() * 6) % 100,
          y: (p.y + Math.random() * 6) % 100,
        };

        setTrail((t) => [...t.slice(-20), newPos]);

        return newPos;
      });

      // status robot
      setRobotStatus("navigating");

      // missions qui évoluent
      setMissions((prev) =>
        prev.map((m) => ({
          ...m,
          status:
            m.status === "idle"
              ? "navigating"
              : m.status === "navigating"
              ? "completed"
              : "idle",
        }))
      );
    }, 1500);

    return () => clearInterval(interval);
  }, []);

  return { robotStatus, missions, position, trail };
};