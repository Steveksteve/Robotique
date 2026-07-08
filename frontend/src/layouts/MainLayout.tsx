import { Outlet } from "react-router-dom";
import Navbar from "../components/Navbar";

export default function MainLayout() {
  return (
    <div style={layout}>
      <Navbar />

      <div style={content}>
        <Outlet />
      </div>
    </div>
  );
}

const layout = {
  minHeight: "100vh",
  background: "#020617",
  color: "white",
};

const content = {
  padding: "40px",
};