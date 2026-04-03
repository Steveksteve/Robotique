#!/bin/bash

# TYPES
cat << 'EOT' > src/types/mission.ts
export type MissionStatus = "created" | "navigating" | "completed" | "error";

export interface Mission {
  id: string;
  from: string;
  to: string;
  status: MissionStatus;
}
EOT

# HOOK
cat << 'EOT' > src/hooks/useWebSocket.ts
import { Mission } from "../types/mission";

export const useWebSocket = () => {
  // MOCK DATA (remplacé plus tard par websocket)
  const missions: Mission[] = [
    { id: "1", from: "A", to: "B", status: "created" },
    { id: "2", from: "Stock", to: "Desk", status: "navigating" },
  ];

  const robotStatus = "idle";

  return { missions, robotStatus };
};
EOT

# NAVBAR
cat << 'EOT' > src/components/Navbar.tsx
import { Link } from "react-router-dom";

export default function Navbar() {
  return (
    <nav style={{ padding: 20, borderBottom: "1px solid #ddd" }}>
      <Link to="/">Dashboard</Link> |{" "}
      <Link to="/missions">Missions</Link>
    </nav>
  );
}
EOT

# LAYOUT
cat << 'EOT' > src/layouts/MainLayout.tsx
import Navbar from "../components/Navbar";

export default function MainLayout({ children }: any) {
  return (
    <>
      <Navbar />
      <div style={{ padding: 20 }}>{children}</div>
    </>
  );
}
EOT

# ROBOT STATUS
cat << 'EOT' > src/components/RobotStatus.tsx
export default function RobotStatus({ status }: { status: string }) {
  return (
    <div>
      <h2>Robot Status</h2>
      <p>{status}</p>
    </div>
  );
}
EOT

# MISSION CARD
cat << 'EOT' > src/components/MissionCard.tsx
import { Mission } from "../types/mission";

export default function MissionCard({ mission }: { mission: Mission }) {
  return (
    <div style={{ border: "1px solid #ccc", padding: 10, marginBottom: 10 }}>
      <p>ID: {mission.id}</p>
      <p>{mission.from} → {mission.to}</p>
      <p>Status: {mission.status}</p>
    </div>
  );
}
EOT

# DASHBOARD
cat << 'EOT' > src/pages/Dashboard.tsx
import { useWebSocket } from "../hooks/useWebSocket";
import RobotStatus from "../components/RobotStatus";

export default function Dashboard() {
  const { robotStatus } = useWebSocket();

  return (
    <div>
      <h1>Dashboard</h1>
      <RobotStatus status={robotStatus} />
    </div>
  );
}
EOT

# MISSIONS
cat << 'EOT' > src/pages/Missions.tsx
import { useWebSocket } from "../hooks/useWebSocket";
import MissionCard from "../components/MissionCard";

export default function Missions() {
  const { missions } = useWebSocket();

  return (
    <div>
      <h1>Missions</h1>
      {missions.map((m) => (
        <MissionCard key={m.id} mission={m} />
      ))}
    </div>
  );
}
EOT

# NOT FOUND
cat << 'EOT' > src/pages/NotFound.tsx
export default function NotFound() {
  return <h1>404</h1>;
}
EOT

# APP
cat << 'EOT' > src/App.tsx
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import Missions from "./pages/Missions";
import NotFound from "./pages/NotFound";
import MainLayout from "./layouts/MainLayout";

function App() {
  return (
    <BrowserRouter>
      <MainLayout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/missions" element={<Missions />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </MainLayout>
    </BrowserRouter>
  );
}

export default App;
EOT

echo "DONE"
