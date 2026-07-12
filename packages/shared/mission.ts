export const MISSION_FLOW = [
  "CREATED",
  "ASSIGNED",
  "NAVIGATING_TO_PICKUP",
  "SCANNING_QR",
  "PICKING_UP",
  "NAVIGATING_TO_DROP",
  "DROPPING_OFF",
  "COMPLETED",
] as const;

export type MissionStatus = (typeof MISSION_FLOW)[number] | "ERROR";

export const TERMINAL_MISSION_STATUSES: MissionStatus[] = ["COMPLETED", "ERROR"];
