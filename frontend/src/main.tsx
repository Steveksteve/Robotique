type Point = {
  x: number;
  y: number;
};

type Props = {
  x: number;
  y: number;
  trail: Point[];
};

export default function MiniMap({ x, y, trail }: Props) {
  return (
    <div style={map}>
      {trail.map((p, i) => (
        <div
          key={i}
          style={{
            ...dot,
            left: p.x,
            top: p.y,
            opacity: 0.3,
          }}
        />
      ))}

      <div
        style={{
          ...robot,
          left: x,
          top: y,
        }}
      />
    </div>
  );
}

/* ---------- STYLE ---------- */

const map = {
  width: 320,
  height: 320,
  border: "1px solid #38bdf8",
  borderRadius: 12,
  position: "relative" as const,
};

const dot = {
  width: 6,
  height: 6,
  borderRadius: "50%",
  position: "absolute" as const,
  background: "#64748b",
};

const robot = {
  width: 10,
  height: 10,
  borderRadius: "50%",
  position: "absolute" as const,
  background: "#22d3ee",
};