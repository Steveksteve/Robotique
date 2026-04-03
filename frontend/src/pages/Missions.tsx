import { useWebSocket } from "../hooks/useWebSocket";

export default function Missions() {
  const { missions } = useWebSocket();

  return (
    <div style={container}>
      <h1 style={title}>Mission Feed</h1>

      {missions.map((m) => (
        <div key={m.id} style={card}>
          <div>
            <div style={route}>
              {m.from} → {m.to}
            </div>
            <div style={sub}>{m.status}</div>
          </div>

          <div style={badge(m.status)}>{m.status}</div>
        </div>
      ))}
    </div>
  );
}

const container = { padding: "60px" };

const title = { fontSize: 32, marginBottom: 30 };

const card = {
  display: "flex",
  justifyContent: "space-between",
  padding: 20,
  marginBottom: 12,
  borderRadius: 10,
  background: "rgba(255,255,255,0.02)",
  border: "1px solid rgba(255,255,255,0.05)",
};

const route = { fontWeight: 500 };

const sub = { fontSize: 12, color: "#64748b" };

const badge = (status: string) => ({
  padding: "6px 10px",
  borderRadius: 6,
  fontSize: 12,
  background:
    status === "completed"
      ? "#22c55e20"
      : status === "navigating"
      ? "#38bdf820"
      : "#64748b20",
});