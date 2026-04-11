import { useWebSocket } from "../hooks/useWebSocket";
import type { Mission } from "../types/mission";

export default function Missions() {
  const { missions } = useWebSocket();

  return (
    <div style={container}>
      <h1 style={title}>Mission Control</h1>

      <div style={list}>
        {missions.map((mission: Mission) => (
          <div key={mission.id} style={card}>
            <div style={left}>
              <div style={path}>
                {mission.origin} {"->"} {mission.destination}
              </div>

              <div style={meta}>
                Mission #{mission.id}
                {mission.object ? ` - ${mission.object}` : ""}
              </div>
            </div>

            <div style={status(mission.status)}>{mission.status}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

const container = {
  padding: "60px",
  color: "white",
};

const title = {
  fontSize: 28,
  marginBottom: 30,
};

const list = {
  display: "flex",
  flexDirection: "column" as const,
  gap: 20,
};

const card = {
  display: "flex",
  justifyContent: "space-between",
  alignItems: "center",
  padding: "20px 24px",
  borderRadius: 12,
  background: "rgba(255,255,255,0.03)",
  border: "1px solid rgba(255,255,255,0.05)",
  backdropFilter: "blur(6px)",
};

const left = {
  display: "flex",
  flexDirection: "column" as const,
  gap: 6,
};

const path = {
  fontSize: 16,
  fontWeight: 500,
};

const meta = {
  fontSize: 12,
  color: "#64748b",
};

const status = (value: string) => ({
  padding: "6px 12px",
  borderRadius: 8,
  fontSize: 12,
  textTransform: "uppercase" as const,
  background:
    value === "COMPLETED"
      ? "rgba(34,197,94,0.15)"
      : value.includes("NAVIGATING") || value === "ASSIGNED"
      ? "rgba(56,189,248,0.15)"
      : value === "FAILED" || value === "CANCELLED" || value === "EMERGENCY_STOPPED"
      ? "rgba(239,68,68,0.15)"
      : "rgba(100,116,139,0.15)",
  color:
    value === "COMPLETED"
      ? "#22c55e"
      : value.includes("NAVIGATING") || value === "ASSIGNED"
      ? "#38bdf8"
      : value === "FAILED" || value === "CANCELLED" || value === "EMERGENCY_STOPPED"
      ? "#ef4444"
      : "#64748b",
});
