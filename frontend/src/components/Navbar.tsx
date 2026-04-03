import { Link, useLocation } from "react-router-dom";

export default function Navbar() {
  const { pathname } = useLocation();

  return (
    <div style={nav}>
      <div style={logo}>ROBOT SYSTEM</div>

      <div style={links}>
        <Link style={link(pathname === "/")} to="/">
          Dashboard
        </Link>
        <Link style={link(pathname === "/missions")} to="/missions">
          Missions
        </Link>
      </div>
    </div>
  );
}

const nav = {
  display: "flex",
  justifyContent: "space-between",
  alignItems: "center",
  padding: "20px 40px",
  borderBottom: "1px solid rgba(255,255,255,0.05)",
  background: "rgba(2,6,23,0.7)",
  backdropFilter: "blur(10px)",
};

const logo = {
  fontWeight: 600,
  letterSpacing: 2,
  fontSize: 13,
  color: "#38bdf8",
};

const links = {
  display: "flex",
  gap: 16,
};

const link = (active: boolean) => ({
  padding: "6px 12px",
  borderRadius: 8,
  fontSize: 13,
  background: active ? "#38bdf820" : "transparent",
  color: active ? "#38bdf8" : "#64748b",
});