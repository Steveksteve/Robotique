export type MissionStatus =
  | "CREATED"
  | "ASSIGNED"
  | "NAVIGATING_TO_PICKUP"
  | "SCANNING_QR"
  | "PICKING_UP"
  | "NAVIGATING_TO_DROP"
  | "DROPPING_OFF"
  | "COMPLETED"
  | "ERROR";

export interface Mission {
  id: number;
  origin: string;
  destination: string;
  object?: string;
  expected_qr?: string;
  pickup_x?: number | null;
  pickup_y?: number | null;
  pickup_theta?: number | null;
  dropoff_x?: number | null;
  dropoff_y?: number | null;
  dropoff_theta?: number | null;
  status: MissionStatus;
  error_reason?: string | null;
  created_at?: string;
  updated_at?: string;
}

export interface Position {
  x: number;
  y: number;
}

export interface RealtimeEvent {
  type: string;
  message: string;
  timestamp: string;
}

export const MISSION_STATUS_LABELS: Record<MissionStatus, string> = {
  CREATED: "Créée",
  ASSIGNED: "Envoyée au robot",
  NAVIGATING_TO_PICKUP: "Navigation vers point A",
  SCANNING_QR: "Scan QR",
  PICKING_UP: "Prise objet",
  NAVIGATING_TO_DROP: "Navigation vers point B",
  DROPPING_OFF: "Dépôt objet",
  COMPLETED: "Terminée",
  ERROR: "Erreur",
};

export const MISSION_STATUS_ORDER: MissionStatus[] = [
  "CREATED",
  "ASSIGNED",
  "NAVIGATING_TO_PICKUP",
  "SCANNING_QR",
  "PICKING_UP",
  "NAVIGATING_TO_DROP",
  "DROPPING_OFF",
  "COMPLETED",
];
