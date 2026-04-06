import { Link, useLocation } from "react-router-dom";

export default function Navbar() {
  const { pathname } = useLocation();

  return (
    <div style={nav}>
      <div style={logo}>ROBOT CORE</div>

      <div style={links}>
        <Link style={link(pathname === "/")} to="/">Dashboard</Link>
        <Link style={link(pathname === "/missions")} to="/missions">Missions</Link>
      </div>
    </div>
  );
}

const nav = {
  display: "flex",
  justifyContent: "space-between",
  padding: "20px 40px",
  borderBottom: "1px solid rgba(56,189,248,0.1)",
};

const logo = {
  color: "#38bdf8",
  fontWeight: 700,
  letterSpacing: 2,
};

const links = {
  display: "flex",
  gap: 30,
};

const link = (active: boolean) => ({
  color: active ? "#38bdf8" : "#64748b",
  textDecoration: "none",
});