import { useEffect, useState } from "react";
import type { FormEvent } from "react";
import type { Mission } from "../types/mission";

const API_BASE = import.meta.env.VITE_API_BASE ?? "/api";

export default function Missions() {
  const [missions, setMissions] = useState<Mission[]>([]);
  const [origin, setOrigin] = useState("");
  const [destination, setDestination] = useState("");
  const [object, setObject] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function fetchMissions() {
    try {
      setError("");

      const response = await fetch(`${API_BASE}/missions`);

      if (!response.ok) {
        throw new Error("Impossible de charger les missions.");
      }

      const data = await response.json();
      setMissions(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erreur inconnue.");
    }
  }

  async function createMission(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!origin.trim() || !destination.trim() || !object.trim()) {
      setError("Tous les champs sont obligatoires.");
      return;
    }

    try {
      setLoading(true);
      setError("");

      const response = await fetch(`${API_BASE}/missions`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          origin,
          destination,
          object,
        }),
      });

      if (!response.ok) {
        throw new Error("Impossible de créer la mission.");
      }

      setOrigin("");
      setDestination("");
      setObject("");

      await fetchMissions();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erreur inconnue.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void fetchMissions();
  }, []);

  return (
    <div style={container}>
      <h1 style={title}>Mission Control</h1>

      <form style={form} onSubmit={createMission}>
        <h2 style={subtitle}>Créer une mission</h2>

        <input
          style={input}
          type="text"
          placeholder="Origine ex: Stock A"
          value={origin}
          onChange={(event) => setOrigin(event.target.value)}
        />

        <input
          style={input}
          type="text"
          placeholder="Destination ex: SAV"
          value={destination}
          onChange={(event) => setDestination(event.target.value)}
        />

        <input
          style={input}
          type="text"
          placeholder="Objet ex: Colis #42"
          value={object}
          onChange={(event) => setObject(event.target.value)}
        />

        <button style={button} type="submit" disabled={loading}>
          {loading ? "Création..." : "Créer la mission"}
        </button>

        {error && <div style={errorBox}>{error}</div>}
      </form>

      <div style={header}>
        <h2 style={subtitle}>Liste des missions</h2>
        <button style={refreshButton} onClick={fetchMissions}>
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
                </div>
              </div>

              <div style={status(mission.status)}>{mission.status}</div>
            </div>
          ))
        )}
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

const subtitle = {
  fontSize: 20,
  margin: 0,
};

const form = {
  display: "grid",
  gap: 14,
  maxWidth: 520,
  marginBottom: 40,
  padding: 24,
  borderRadius: 16,
  background: "rgba(255,255,255,0.03)",
  border: "1px solid rgba(56,189,248,0.15)",
};

const input = {
  padding: "12px 14px",
  borderRadius: 10,
  border: "1px solid rgba(255,255,255,0.12)",
  background: "#020617",
  color: "white",
  outline: "none",
};

const button = {
  padding: "12px 14px",
  borderRadius: 10,
  border: "none",
  background: "#38bdf8",
  color: "#020617",
  fontWeight: 700,
  cursor: "pointer",
};

const refreshButton = {
  padding: "10px 14px",
  borderRadius: 10,
  border: "1px solid rgba(56,189,248,0.3)",
  background: "transparent",
  color: "#38bdf8",
  cursor: "pointer",
};

const errorBox = {
  padding: 12,
  borderRadius: 10,
  background: "rgba(239,68,68,0.15)",
  color: "#f87171",
};

const header = {
  display: "flex",
  justifyContent: "space-between",
  alignItems: "center",
  marginBottom: 20,
};

const list = {
  display: "flex",
  flexDirection: "column" as const,
  gap: 20,
};

const empty = {
  color: "#64748b",
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
});