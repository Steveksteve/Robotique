export type MissionStatus = "created" | "navigating" | "completed";

export interface Mission {
  id: number;
  from: string;
  to: string;
  status: MissionStatus;
}

export interface Position {
  x: number;
  y: number;
}