export default function Radar() {
  return (
    <div style={container}>
      <div style={pulse} />
      <div style={ring} />
      <div style={ring2} />
    </div>
  );
}

const container = {
  width: 120,
  height: 120,
  borderRadius: "50%",
  position: "relative" as const,
  border: "1px solid rgba(56,189,248,0.2)",
};

const pulse = {
  position: "absolute" as const,
  inset: 0,
  borderRadius: "50%",
  animation: "radar 2s infinite",
  border: "2px solid #38bdf8",
};

const ring = {
  position: "absolute" as const,
  inset: 20,
  borderRadius: "50%",
  border: "1px solid rgba(255,255,255,0.1)",
};

const ring2 = {
  position: "absolute" as const,
  inset: 40,
  borderRadius: "50%",
  border: "1px solid rgba(255,255,255,0.05)",
};