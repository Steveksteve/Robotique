import { useEffect, useState } from "react";
import type { CSSProperties, FormEvent } from "react";
import { useWebSocket } from "../hooks/useWebSocket";
import type { Mission } from "../types/mission";
import { MISSION_STATUS_LABELS } from "../types/mission";

const API_BASE = import.meta.env.VITE_API_BASE ?? "/api";

type CreateMissionResponse = {
  mission_id: number;
  mission?: Mission;
};

export default function Missions() {
  const realtime = useWebSocket();

  const [missions, setMissions] = useState<Mission[]>([]);
  const [origin, setOrigin] = useState("");
  const [destination, setDestination] = useState("");
  const [objectName, setObjectName] = useState("");
  const [expectedQr, setExpectedQr] = useState("a");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [info, setInfo] = useState("");

  async function fetchMissions() {
    try {
      setError("");

      const response = await fetch(`${API_BASE}/missions`);

      if (!response.ok) {
        throw new Error("Impossible de charger les missions.");
      }

      const data = (await response.json()) as Mission[];

      setMissions(
        data
          .map((mission) => ({
            ...mission,
            id: Number(mission.id),
          }))
          .sort((a, b) => b.id - a.id),
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erreur inconnue.");
    }
  }

  async function createMission(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!origin.trim() || !destination.trim() || !objectName.trim() || !expectedQr.trim()) {
      setError("Tous les champs sont obligatoires.");
      return;
    }

    try {
      setLoading(true);
      setError("");
      setInfo("");

      const response = await fetch(`${API_BASE}/missions`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          origin: origin.trim(),
          destination: destination.trim(),
          object: objectName.trim(),
          expected_qr: expectedQr.trim(),
        }),
      });

      if (!response.ok) {
        throw new Error("Impossible de créer la mission.");
      }

      const created = (await response.json()) as CreateMissionResponse;

      setOrigin("");
      setDestination("");
      setObjectName("");
      setExpectedQr("a");

      await fetchMissions();

      const sent = realtime.assignMission(Number(created.mission_id));

      setInfo(
        sent
          ? `Mission #${created.mission_id} créée et envoyée au robot.`
          : `Mission #${created.mission_id} créée, mais le WebSocket n’est pas connecté.`,
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erreur inconnue.");
    } finally {
      setLoading(false);
    }
  }

  function assignMission(missionId: number) {
    setError("");
    setInfo("");

    const sent = realtime.assignMission(missionId);

    if (sent) {
      setInfo(`Mission #${missionId} envoyée au robot.`);
    } else {
      setError("Impossible d’envoyer la mission : WebSocket non connecté.");
    }
  }

  function emergencyStop(missionId: number) {
    setError("");
    setInfo("");

    const sent = realtime.emergencyStop(missionId);

    if (sent) {
      setInfo(`Arrêt d’urgence demandé pour la mission #${missionId}.`);
    } else {
      setError("Impossible d’envoyer l’arrêt d’urgence : WebSocket non connecté.");
    }
  }

  useEffect(() => {
    void fetchMissions();
  }, []);

  useEffect(() => {
    if (realtime.missions.length > 0) {
      setMissions(realtime.missions);
    }
  }, [realtime.missions]);

  return (
    <div style={container}>
      <h1 style={title}>Mission Control</h1>

      <div style={wsBox}>
        <span>
          WebSocket :{" "}
          <strong style={wsStatus(realtime.connectionStatus)}>
            {realtime.connectionStatus}
          </strong>
        </span>

        <span style={robotText}>Robot : {realtime.robotStatus}</span>
      </div>

      <form style={form} onSubmit={createMission}>
        <h2 style={subtitle}>Créer une mission</h2>

        <label style={label}>
          Origine
          <input
            style={input}
            type="text"
            placeholder="Ex : Stock A"
            value={origin}
            onChange={(event) => setOrigin(event.target.value)}
          />
        </label>

        <label style={label}>
          Destination
          <input
            style={input}
            type="text"
            placeholder="Ex : SAV"
            value={destination}
            onChange={(event) => setDestination(event.target.value)}
          />
        </label>

        <label style={label}>
          Objet à transporter
          <input
            style={input}
            type="text"
            placeholder="Ex : Colis #42"
            value={objectName}
            onChange={(event) => setObjectName(event.target.value)}
          />
        </label>

        <label style={label}>
          QR attendu
          <input
            style={input}
            type="text"
            placeholder="Ex : a"
            value={expectedQr}
            onChange={(event) => setExpectedQr(event.target.value)}
          />
        </label>

        <button style={button} type="submit" disabled={loading}>
          {loading ? "Création..." : "Créer + envoyer au robot"}
        </button>

        {error && (
          <div style={errorBox} role="alert">
            {error}
          </div>
        )}

        {info && <div style={infoBox}>{info}</div>}
      </form>

      <div style={header}>
        <h2 style={subtitle}>Liste des missions</h2>

        <button style={refreshButton} onClick={fetchMissions} type="button">
          Rafraîchir
        </button>
      </div>

      <div style={list}>
        {missions.length === 0 ? (
          <div style={empty}>Aucune mission pour le moment.</div>
        ) : (
          missions.map((mission) => (
            <div key={mission.id} style={card}>
              <div style={left}>
                <div style={path}>
                  {mission.origin} {"->"} {mission.destination}
                </div>

                <div style={meta}>
                  Mission #{mission.id}
                  {mission.object ? ` - ${mission.object}` : ""}
                  {mission.expected_qr ? ` - QR: ${mission.expected_qr}` : ""}
                </div>
              </div>

              <div style={actions}>
                {mission.status === "CREATED" && (
                  <button
                    type="button"
                    style={secondaryButton}
                    onClick={() => assignMission(Number(mission.id))}
                    disabled={realtime.connectionStatus !== "connected"}
                  >
                    Envoyer au robot
                  </button>
                )}

                {!["COMPLETED", "ERROR"].includes(mission.status) && (
                  <button
                    type="button"
                    style={dangerButton}
                    onClick={() => emergencyStop(Number(mission.id))}
                    disabled={realtime.connectionStatus !== "connected"}
                  >
                    Stop
                  </button>
                )}

                <div style={statusStyle(mission.status)}>{MISSION_STATUS_LABELS[mission.status] ?? mission.status}</div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

const container: CSSProperties = {
  padding: "60px",
  color: "white",
};

const title: CSSProperties = {
  fontSize: 28,
  marginBottom: 20,
};

const subtitle: CSSProperties = {
  fontSize: 20,
  margin: 0,
};

const wsBox: CSSProperties = {
  display: "flex",
  alignItems: "center",
  gap: 16,
  marginBottom: 24,
  padding: "12px 16px",
  borderRadius: 10,
  background: "rgba(255,255,255,0.03)",
  border: "1px solid rgba(255,255,255,0.08)",
  width: "fit-content",
};

const robotText: CSSProperties = {
  color: "#94a3b8",
};

function wsStatus(value: string): CSSProperties {
  return {
    color:
      value === "connected"
        ? "#22c55e"
        : value === "connecting"
          ? "#f59e0b"
          : "#ef4444",
  };
}

const form: CSSProperties = {
  display: "grid",
  gap: 14,
  maxWidth: 520,
  marginBottom: 40,
  padding: 24,
  borderRadius: 16,
  background: "rgba(255,255,255,0.03)",
  border: "1px solid rgba(56,189,248,0.15)",
};

const label: CSSProperties = {
  display: "grid",
  gap: 8,
  fontSize: 13,
  color: "#94a3b8",
};

const input: CSSProperties = {
  padding: "12px 14px",
  borderRadius: 10,
  border: "1px solid rgba(255,255,255,0.12)",
  background: "#020617",
  color: "white",
  outline: "none",
};

const button: CSSProperties = {
  padding: "12px 14px",
  borderRadius: 10,
  border: "none",
  background: "#38bdf8",
  color: "#020617",
  fontWeight: 700,
  cursor: "pointer",
};

const refreshButton: CSSProperties = {
  padding: "10px 14px",
  borderRadius: 10,
  border: "1px solid rgba(56,189,248,0.3)",
  background: "transparent",
  color: "#38bdf8",
  cursor: "pointer",
};

const secondaryButton: CSSProperties = {
  padding: "8px 10px",
  borderRadius: 8,
  border: "1px solid rgba(56,189,248,0.35)",
  background: "rgba(56,189,248,0.08)",
  color: "#7dd3fc",
  cursor: "pointer",
};

const dangerButton: CSSProperties = {
  padding: "8px 10px",
  borderRadius: 8,
  border: "1px solid rgba(248,113,113,0.45)",
  background: "rgba(239,68,68,0.1)",
  color: "#fca5a5",
  cursor: "pointer",
};

const errorBox: CSSProperties = {
  padding: 12,
  borderRadius: 10,
  background: "rgba(239,68,68,0.15)",
  color: "#f87171",
};

const infoBox: CSSProperties = {
  padding: 12,
  borderRadius: 10,
  background: "rgba(34,197,94,0.12)",
  color: "#86efac",
};

const header: CSSProperties = {
  display: "flex",
  justifyContent: "space-between",
  alignItems: "center",
  marginBottom: 20,
};

const list: CSSProperties = {
  display: "flex",
  flexDirection: "column",
  gap: 20,
};

const empty: CSSProperties = {
  color: "#64748b",
};

const card: CSSProperties = {
  display: "flex",
  justifyContent: "space-between",
  alignItems: "center",
  gap: 18,
  padding: "20px 24px",
  borderRadius: 12,
  background: "rgba(255,255,255,0.03)",
  border: "1px solid rgba(255,255,255,0.05)",
  backdropFilter: "blur(6px)",
};

const left: CSSProperties = {
  display: "flex",
  flexDirection: "column",
  gap: 6,
};

const actions: CSSProperties = {
  display: "flex",
  alignItems: "center",
  gap: 10,
};

const path: CSSProperties = {
  fontSize: 16,
  fontWeight: 500,
};

const meta: CSSProperties = {
  fontSize: 12,
  color: "#64748b",
};

function statusStyle(value: string): CSSProperties {
  return {
    padding: "6px 12px",
    borderRadius: 8,
    fontSize: 12,
    textTransform: "uppercase",
    background:
      value === "COMPLETED"
        ? "rgba(34,197,94,0.15)"
        : value === "ERROR"
          ? "rgba(239,68,68,0.15)"
          : value.includes("NAVIGATING") || value === "ASSIGNED"
            ? "rgba(56,189,248,0.15)"
            : "rgba(100,116,139,0.15)",
    color:
      value === "COMPLETED"
        ? "#22c55e"
        : value === "ERROR"
          ? "#ef4444"
          : value.includes("NAVIGATING") || value === "ASSIGNED"
            ? "#38bdf8"
            : "#64748b",
  };
}