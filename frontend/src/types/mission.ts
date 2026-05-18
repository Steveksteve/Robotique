export type MissionStatus =
  | "CREATED"
  | "ASSIGNED"
  | "NAVIGATING_TO_PICKUP"
  | "PICKING_UP"
  | "NAVIGATING_TO_DROP"
  | "COMPLETED"
  | "ERROR";

export interface Mission {
  id: number;
  origin: string;
  destination: string;
  object?: string;
  status: MissionStatus;
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