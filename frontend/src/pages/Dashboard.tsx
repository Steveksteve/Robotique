import MiniMap from "../components/MiniMap";
import { useWebSocket } from "../hooks/useWebSocket";

export default function Dashboard() {
  const {
    connectionStatus,
    robotStatus,
    emergencyActive,
    missions,
    position,
    trail,
    lastHeartbeat,
    events,
    emergencyStop,
  } = useWebSocket();

  const activeMission = missions.find(
    (mission) => !["COMPLETED", "ERROR"].includes(mission.status),
  );

  return (
    <div>
      <div style={topbar}>
        <h1 style={title}>Control Center</h1>

        <button
          style={emergencyButton}
          type="button"
          onClick={() => emergencyStop(activeMission?.id)}
          disabled={connectionStatus !== "connected"}
          aria-label="Déclencher l’arrêt d’urgence du robot"
        >
          ARRÊT D’URGENCE
        </button>
      </div>

      {emergencyActive && (
        <div style={alertBox} role="alert">
          Arrêt d’urgence actif. La mission en cours est passée en erreur ou attend une reprise côté robot.
        </div>
      )}

      <div style={grid}>
        <div style={cardBig}>
          <div style={cardTitle}>POSITION TRACKING</div>
          <MiniMap x={position.x} y={position.y} trail={trail} />
        </div>

        <div style={card}>
          <div style={cardTitle}>WEBSOCKET</div>
          <div style={value}>{connectionStatus}</div>
        </div>

        <div style={card}>
          <div style={cardTitle}>ROBOT STATUS</div>
          <div style={value}>{robotStatus}</div>
        </div>

        <div style={card}>
          <div style={cardTitle}>COORDINATES</div>
          <div style={value}>
            X: {position.x}
            <br />
            Y: {position.y}
          </div>
        </div>

        <div style={card}>
          <div style={cardTitle}>MISSIONS</div>
          <div style={value}>{missions.length}</div>
        </div>

        <div style={card}>
          <div style={cardTitle}>MISSION ACTIVE</div>
          <div style={smallValue}>
            {activeMission ? `#${activeMission.id} - ${activeMission.status}` : "aucune"}
          </div>
        </div>

        <div style={card}>
          <div style={cardTitle}>LAST HEARTBEAT</div>
          <div style={smallValue}>{lastHeartbeat ?? "none"}</div>
        </div>

        <div style={cardWide}>
          <div style={cardTitle}>LIVE EVENTS</div>
          <div style={feed}>
            {events.length === 0 ? (
              <div style={feedItem}>No events received yet.</div>
            ) : (
              events.map((event) => (
                <div key={`${event.type}-${event.timestamp}-${event.message}`} style={feedItem}>
                  <strong>{event.type}</strong>
                  <div>{event.message}</div>
                  <small style={timestamp}>{event.timestamp}</small>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

const topbar = {
  display: "flex",
  justifyContent: "space-between",
  alignItems: "center",
  gap: 20,
  marginBottom: 30,
};

const title = {
  fontSize: 32,
  margin: 0,
};

const emergencyButton = {
  padding: "14px 18px",
  borderRadius: 12,
  border: "1px solid rgba(248,113,113,0.7)",
  background: "rgba(239,68,68,0.18)",
  color: "#fecaca",
  fontWeight: 800,
  cursor: "pointer",
};

const alertBox = {
  marginBottom: 24,
  padding: "14px 16px",
  borderRadius: 12,
  border: "1px solid rgba(248,113,113,0.4)",
  background: "rgba(239,68,68,0.12)",
  color: "#fecaca",
};

const grid = {
  display: "grid",
  gridTemplateColumns: "2fr 1fr 1fr",
  gap: 30,
};

const cardBig = {
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

const cardWide = {
  gridColumn: "1 / -1",
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

const smallValue = {
  fontSize: 14,
  fontWeight: 500,
  wordBreak: "break-word" as const,
};

const feed = {
  display: "grid",
  gap: 12,
};

const feedItem = {
  padding: "12px 14px",
  borderRadius: 10,
  background: "rgba(15,23,42,0.8)",
  border: "1px solid rgba(56,189,248,0.1)",
};

const timestamp = {
  color: "#64748b",
};