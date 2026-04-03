import { useWebSocket } from "../hooks/useWebSocket";

export default function Dashboard() {
  const { robotStatus, position, missions } = useWebSocket();

  return (
    <div style={container}>
      <h1 style={title}>Robot Dashboard</h1>

      {/* STATUS */}
      <div style={card}>
        <div style={label}>Status</div>
        <div style={status(robotStatus)}>
          {robotStatus}
        </div>
      </div>

      {/* POSITION */}
      <div style={card}>
        <div style={label}>Position</div>
        <div style={value}>
          X: {position.x} | Y: {position.y}
        </div>
      </div>

      {/* MISSIONS */}
      <div style={card}>
        <div style={label}>Missions</div>

        {missions.map((m) => (
          <div key={m.id} style={mission}>
            {m.from} → {m.to}
            <span style={badge(m.status)}>{m.status}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

/* ---------- STYLE ---------- */

const container = {
  padding: "60px",
  display: "flex",
  flexDirection: "column" as const,
  gap: 20,
};

const title = {
  fontSize: 28,
  marginBottom: 20,
};

const card = {
  padding: 20,
  borderRadius: 10,
  background: "rgba(255,255,255,0.02)",
  border: "1px solid rgba(255,255,255,0.05)",
};

const label = {
  fontSize: 12,
  color: "#64748b",
  marginBottom: 10,
};

const value = {
  fontSize: 18,
};

const status = (s: string) => ({
  fontSize: 18,
  color: s === "active" ? "#22c55e" : "#64748b",
});

const mission = {
  display: "flex",
  justifyContent: "space-between",
  marginBottom: 8,
};

const badge = (status: string) => ({
  fontSize: 12,
  padding: "2px 6px",
  borderRadius: 6,
  background:
    status === "completed"
      ? "#22c55e20"
      : status === "navigating"
      ? "#38bdf820"
      : "#64748b20",
});