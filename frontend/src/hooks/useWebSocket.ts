import { useEffect, useSyncExternalStore } from "react";
import type { Mission, MissionStatus, Position, RealtimeEvent } from "../types/mission";

type ConnectionStatus = "connecting" | "connected" | "disconnected";

type RealtimeState = {
  connectionStatus: ConnectionStatus;
  robotStatus: string;
  emergencyActive: boolean;
  lastHeartbeat: string | null;
  position: Position;
  missions: Mission[];
  trail: Position[];
  events: RealtimeEvent[];
};

type MissionUpdatedEvent = {
  type:
    | "mission:updated"
    | "mission.status_updated"
    | "mission:completed"
    | "mission.completed"
    | "mission:assigned";
  mission_id: number;
  status?: MissionStatus;
  mission?: Partial<Mission> & { id?: number };
  message?: string;
  timestamp?: string;
};

type PositionEvent = {
  type: "robot:position" | "robot.position_updated";
  mission_id?: number | null;
  x: number;
  y: number;
  timestamp?: string;
};

type HeartbeatEvent = {
  type: "robot.heartbeat";
  robot_id?: string;
  mission_id?: number;
  timestamp?: string;
};

type SafetyEvent = {
  type: "robot:emergency_stop" | "robot.timeout";
  robot_id?: string;
  mission_id?: number | null;
  reason?: string;
  message?: string;
  mission?: Partial<Mission> & { id?: number };
  timestamp?: string;
};

type ServerEvent = {
  type:
    | "server.ack"
    | "server.error"
    | "robot.connected"
    | "robot.disconnected"
    | "dashboard:resync";
  message?: string;
  robot_id?: string;
  timestamp?: string;
};

type IncomingEvent =
  | MissionUpdatedEvent
  | PositionEvent
  | HeartbeatEvent
  | SafetyEvent
  | ServerEvent;

const WS_URL = import.meta.env.VITE_WS_URL || `${window.location.protocol === "https:" ? "wss" : "ws"}://${window.location.host}/ws`;
const API_BASE = import.meta.env.VITE_API_BASE ?? "/api";
const MAX_TRAIL = 24;
const MAX_EVENTS = 16;

let socket: WebSocket | null = null;
let reconnectTimer: number | null = null;
let hasLoadedInitialMissions = false;
let isLoadingInitialMissions = false;

const listeners = new Set<() => void>();

let state: RealtimeState = {
  connectionStatus: "connecting",
  robotStatus: "offline",
  emergencyActive: false,
  lastHeartbeat: null,
  position: { x: 160, y: 160 },
  missions: [],
  trail: [],
  events: [],
};

function emit() {
  listeners.forEach((listener) => listener());
}

function setState(updater: (current: RealtimeState) => RealtimeState) {
  state = updater(state);
  emit();
}

function appendEvent(event: RealtimeEvent) {
  setState((current) => ({
    ...current,
    events: [event, ...current.events].slice(0, MAX_EVENTS),
  }));
}

function upsertMission(update: Partial<Mission> & Pick<Mission, "id">) {
  setState((current) => {
    const existing = current.missions.find((mission) => mission.id === update.id);

    const nextMission: Mission = existing
      ? { ...existing, ...update }
      : {
          id: update.id,
          origin: update.origin ?? "Unknown",
          destination: update.destination ?? "Unknown",
          object: update.object,
          expected_qr: update.expected_qr,
          pickup_x: update.pickup_x,
          pickup_y: update.pickup_y,
          pickup_theta: update.pickup_theta,
          dropoff_x: update.dropoff_x,
          dropoff_y: update.dropoff_y,
          dropoff_theta: update.dropoff_theta,
          status: update.status ?? "CREATED",
          error_reason: update.error_reason,
          created_at: update.created_at,
          updated_at: update.updated_at,
        };

    const filtered = current.missions.filter((mission) => mission.id !== update.id);

    return {
      ...current,
      missions: [nextMission, ...filtered].sort((a, b) => b.id - a.id),
    };
  });
}

function updateMissionFromPayload(payload: MissionUpdatedEvent | SafetyEvent) {
  const missionPayload = payload.mission ?? {};
  const missionId = missionPayload.id ?? payload.mission_id;

  if (!missionId) {
    return;
  }

  const statusFromPayload = "status" in payload ? payload.status : undefined;
  const resolvedStatus =
    payload.type === "mission:completed" || payload.type === "mission.completed"
      ? "COMPLETED"
      : missionPayload.status ?? statusFromPayload;

  upsertMission({
    id: missionId,
    origin: missionPayload.origin,
    destination: missionPayload.destination,
    object: missionPayload.object,
    expected_qr: missionPayload.expected_qr,
    pickup_x: missionPayload.pickup_x,
    pickup_y: missionPayload.pickup_y,
    pickup_theta: missionPayload.pickup_theta,
    dropoff_x: missionPayload.dropoff_x,
    dropoff_y: missionPayload.dropoff_y,
    dropoff_theta: missionPayload.dropoff_theta,
    status: resolvedStatus,
    error_reason: missionPayload.error_reason,
    created_at: missionPayload.created_at,
    updated_at: missionPayload.updated_at,
  });
}

async function loadInitialMissions() {
  if (hasLoadedInitialMissions || isLoadingInitialMissions) {
    return;
  }

  isLoadingInitialMissions = true;

  try {
    const response = await fetch(`${API_BASE}/missions`);

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const missions = (await response.json()) as Mission[];

    setState((current) => ({
      ...current,
      missions: missions
        .map((mission) => ({
          ...mission,
          id: Number(mission.id),
          pickup_x: mission.pickup_x == null ? null : Number(mission.pickup_x),
          pickup_y: mission.pickup_y == null ? null : Number(mission.pickup_y),
          pickup_theta: mission.pickup_theta == null ? null : Number(mission.pickup_theta),
          dropoff_x: mission.dropoff_x == null ? null : Number(mission.dropoff_x),
          dropoff_y: mission.dropoff_y == null ? null : Number(mission.dropoff_y),
          dropoff_theta: mission.dropoff_theta == null ? null : Number(mission.dropoff_theta),
        }))
        .sort((a, b) => b.id - a.id),
    }));

    hasLoadedInitialMissions = true;

    appendEvent({
      type: "dashboard:resync",
      message: `${missions.length} mission(s) synchronisée(s) depuis l’API`,
      timestamp: new Date().toISOString(),
    });
  } catch (error) {
    hasLoadedInitialMissions = false;

    appendEvent({
      type: "server.error",
      message: `Resync missions failed: ${
        error instanceof Error ? error.message : "unknown error"
      }`,
      timestamp: new Date().toISOString(),
    });
  } finally {
    isLoadingInitialMissions = false;
  }
}

function scheduleReconnect() {
  if (reconnectTimer !== null) {
    return;
  }

  reconnectTimer = window.setTimeout(() => {
    reconnectTimer = null;
    connect();
  }, 2000);
}

function sendRealtimeCommand(payload: Record<string, unknown>) {
  if (!socket || socket.readyState !== WebSocket.OPEN) {
    appendEvent({
      type: "server.error",
      message: "Commande impossible : WebSocket non connecté.",
      timestamp: new Date().toISOString(),
    });
    return false;
  }

  socket.send(
    JSON.stringify({
      ...payload,
      timestamp: new Date().toISOString(),
    }),
  );

  return true;
}

function handleIncomingEvent(payload: IncomingEvent) {
  const timestamp = payload.timestamp ?? new Date().toISOString();

  switch (payload.type) {
    case "server.ack":
      appendEvent({
        type: payload.type,
        message: payload.message ?? "Connected to WebSocket server",
        timestamp,
      });
      break;

    case "server.error":
      appendEvent({
        type: payload.type,
        message: payload.message ?? "Unknown server error",
        timestamp,
      });
      break;

    case "dashboard:resync":
      appendEvent({
        type: payload.type,
        message: payload.message ?? "Dashboard synchronized",
        timestamp,
      });
      break;

    case "robot.connected":
      setState((current) => ({
        ...current,
        robotStatus: "connected",
      }));
      appendEvent({
        type: payload.type,
        message: `Robot ${payload.robot_id ?? "unknown"} connected`,
        timestamp,
      });
      break;

    case "robot.disconnected":
      setState((current) => ({
        ...current,
        robotStatus: "disconnected",
      }));
      appendEvent({
        type: payload.type,
        message: `Robot ${payload.robot_id ?? "unknown"} disconnected`,
        timestamp,
      });
      break;

    case "robot.heartbeat":
      setState((current) => ({
        ...current,
        robotStatus: "online",
        lastHeartbeat: timestamp,
      }));
      appendEvent({
        type: payload.type,
        message: `Heartbeat received${payload.robot_id ? ` from ${payload.robot_id}` : ""}`,
        timestamp,
      });
      break;

    case "robot:position":
    case "robot.position_updated":
      setState((current) => ({
        ...current,
        position: { x: payload.x, y: payload.y },
        trail: [...current.trail, { x: payload.x, y: payload.y }].slice(-MAX_TRAIL),
      }));
      appendEvent({
        type: "robot:position",
        message: `Position updated to (${payload.x}, ${payload.y})`,
        timestamp,
      });
      break;

    case "mission:assigned":
      updateMissionFromPayload(payload);
      appendEvent({
        type: payload.type,
        message: payload.message ?? `Mission #${payload.mission_id} envoyée au robot`,
        timestamp,
      });
      break;

    case "mission:updated":
    case "mission.status_updated":
    case "mission:completed":
    case "mission.completed": {
      updateMissionFromPayload(payload);

      const resolvedStatus =
        payload.type === "mission:completed" || payload.type === "mission.completed"
          ? "COMPLETED"
          : payload.mission?.status ?? payload.status;

      appendEvent({
        type:
          payload.type === "mission:completed" || payload.type === "mission.completed"
            ? "mission:completed"
            : "mission:updated",
        message:
          payload.type === "mission:completed" || payload.type === "mission.completed"
            ? `Mission #${payload.mission_id} completed`
            : `Mission #${payload.mission_id} -> ${resolvedStatus ?? "UNKNOWN"}`,
        timestamp,
      });
      break;
    }

    case "robot:emergency_stop":
      updateMissionFromPayload(payload);
      setState((current) => ({
        ...current,
        emergencyActive: true,
        robotStatus: "emergency_stop",
      }));
      appendEvent({
        type: payload.type,
        message: payload.reason ?? payload.message ?? "Arrêt d’urgence déclenché",
        timestamp,
      });
      break;

    case "robot.timeout":
      updateMissionFromPayload(payload);
      setState((current) => ({
        ...current,
        robotStatus: "timeout",
      }));
      appendEvent({
        type: payload.type,
        message: payload.message ?? "Perte heartbeat robot",
        timestamp,
      });
      break;

    default:
      break;
  }
}

function connect() {
  if (
    socket &&
    (socket.readyState === WebSocket.OPEN || socket.readyState === WebSocket.CONNECTING)
  ) {
    return;
  }

  setState((current) => ({
    ...current,
    connectionStatus: "connecting",
  }));

  socket = new WebSocket(WS_URL);

  socket.addEventListener("open", () => {
    setState((current) => ({
      ...current,
      connectionStatus: "connected",
    }));

    socket?.send(JSON.stringify({ type: "identify", client_type: "dashboard" }));
  });

  socket.addEventListener("message", (event) => {
    try {
      const payload = JSON.parse(event.data) as IncomingEvent;
      handleIncomingEvent(payload);
    } catch {
      appendEvent({
        type: "server.error",
        message: `Invalid event payload: ${String(event.data)}`,
        timestamp: new Date().toISOString(),
      });
    }
  });

  socket.addEventListener("close", () => {
    setState((current) => ({
      ...current,
      connectionStatus: "disconnected",
      robotStatus: current.robotStatus === "online" ? "stale" : current.robotStatus,
    }));

    scheduleReconnect();
  });

  socket.addEventListener("error", () => {
    appendEvent({
      type: "server.error",
      message: "WebSocket connection error",
      timestamp: new Date().toISOString(),
    });
  });
}

function subscribe(listener: () => void) {
  listeners.add(listener);

  return () => listeners.delete(listener);
}

function getSnapshot() {
  return state;
}

export function useWebSocket() {
  const snapshot = useSyncExternalStore(subscribe, getSnapshot, getSnapshot);

  useEffect(() => {
    void loadInitialMissions();
    connect();
  }, []);

  return {
    ...snapshot,
    assignMission: (missionId: number, robotId?: string) =>
      sendRealtimeCommand({
        type: "mission:assign",
        mission_id: missionId,
        robot_id: robotId,
      }),
    emergencyStop: (missionId?: number, reason = "Arrêt d’urgence demandé depuis le dashboard") =>
      sendRealtimeCommand({
        type: "robot:emergency_stop",
        mission_id: missionId,
        reason,
      }),
  };
}