export type MissionStatus = "created" | "navigating" | "completed" | "error";

export interface Mission {
  id: string;
  from: string;
  to: string;
  status: MissionStatus;
}