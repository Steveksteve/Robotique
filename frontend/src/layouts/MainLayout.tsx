import { Outlet } from "react-router-dom";
import Navbar from "../components/Navbar";

export default function MainLayout() {
  return (
    <div>
      <Navbar />

      <main
        style={{
          maxWidth: "900px",
          margin: "40px auto",
          padding: "0 20px",
        }}
      >
        <Outlet />
      </main>
    </div>
  );
}