import type { Mission } from "../types/mission";

export default function MissionCard({ mission }: { mission: Mission }) {
  return (
    <div style={{
      border: "1px solid #ccc",
      padding: 15,
      borderRadius: 10,
      marginBottom: 10
    }}>
      <strong>ID:</strong> {mission.id} <br />
      <strong>Route:</strong> {mission.from} → {mission.to} <br />
      <strong>Status:</strong> {mission.status}
    </div>
  );
}