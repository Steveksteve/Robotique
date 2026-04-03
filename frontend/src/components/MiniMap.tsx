type Props = {
  x: number;
  y: number;
  trail: { x: number; y: number }[];
};

export default function MiniMap({ x, y, trail }: Props) {
  return (
    <div style={map}>
      {/* zones */}
      <div style={{ ...zone, left: "10%", top: "10%" }}>A</div>
      <div style={{ ...zone, left: "70%", top: "70%" }}>B</div>

      {/* trail */}
      {trail.map((p, i) => (
        <div
          key={i}
          style={{
            ...trailDot,
            left: `${p.x}%`,
            top: `${p.y}%`,
            opacity: i / trail.length,
          }}
        />
      ))}

      {/* robot */}
      <div
        style={{
          ...robot,
          left: `${x}%`,
          top: `${y}%`,
        }}
      />
    </div>
  );
}

const map = {
  width: 260,
  height: 260,
  borderRadius: 14,
  border: "1px solid rgba(255,255,255,0.1)",
  position: "relative" as const,
  background: "rgba(255,255,255,0.02)",
};

const robot = {
  width: 12,
  height: 12,
  borderRadius: "50%",
  background: "#38bdf8",
  position: "absolute" as const,
  transform: "translate(-50%, -50%)",
  transition: "all 0.4s linear",
  boxShadow: "0 0 10px #38bdf8",
};

const trailDot = {
  width: 6,
  height: 6,
  borderRadius: "50%",
  background: "#38bdf8",
  position: "absolute" as const,
  transform: "translate(-50%, -50%)",
};

const zone = {
  position: "absolute" as const,
  width: 30,
  height: 30,
  borderRadius: 6,
  background: "rgba(255,255,255,0.05)",
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  fontSize: 12,
};