import { useWebSocket } from "../hooks/useWebSocket";
import MiniMap from "../components/MiniMap";

export default function Dashboard() {
  const { robotStatus, missions, position, trail } = useWebSocket();

  return (
    <div>
      <h1 style={title}>Control Center</h1>

      <div style={grid}>
        {/* MAP */}
        <div style={cardBig}>
          <div style={cardTitle}>POSITION TRACKING</div>

          <MiniMap x={position.x} y={position.y} trail={trail} />
        </div>

        {/* STATUS */}
        <div style={card}>
          <div style={cardTitle}>ROBOT STATUS</div>
          <div style={value}>{robotStatus}</div>
        </div>

        {/* COORDS */}
        <div style={card}>
          <div style={cardTitle}>COORDINATES</div>
          <div style={value}>
            X: {position.x} <br />
            Y: {position.y}
          </div>
        </div>

        {/* MISSIONS COUNT */}
        <div style={card}>
          <div style={cardTitle}>MISSIONS</div>
          <div style={value}>{missions.length}</div>
        </div>
      </div>
    </div>
  );
}

/* ---------- STYLE ---------- */

const title = {
  fontSize: 32,
  marginBottom: 40,
};

const grid = {
  display: "grid",
  gridTemplateColumns: "2fr 1fr 1fr",
  gap: 30,
};

const cardBig = {
  gridColumn: "span 1",
  background: "rgba(255,255,255,0.03)",
  padding: 20,
  borderRadius: 16,
  border: "1px solid rgba(56,189,248,0.15)",
};

const card = {
  background: "rgba(255,255,255,0.03)",
  padding: 20,
  borderRadius: 16,
  border: "1px solid rgba(255,255,255,0.05)",
};

const cardTitle = {
  fontSize: 12,
  letterSpacing: 1,
  color: "#64748b",
  marginBottom: 10,
};

const value = {
  fontSize: 22,
  fontWeight: 600,
};