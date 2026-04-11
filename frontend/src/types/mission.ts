export type MissionStatus =
  | "CREATED"
  | "ASSIGNED"
  | "NAVIGATING_TO_PICKUP"
  | "PICKING_UP"
  | "NAVIGATING_TO_DROP"
  | "DROPPING_OFF"
  | "COMPLETED"
  | "CANCELLED"
  | "FAILED"
  | "EMERGENCY_STOPPED";

export interface Mission {
  id: number;
  origin: string;
  destination: string;
  object?: string;
  status: MissionStatus;
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
