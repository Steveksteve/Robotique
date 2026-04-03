type Props = {
  status: string;
};

export default function RobotStatus({ status }: Props) {
  const isActive = status === "navigating";

  return (
    <div style={container}>
      <div
        style={{
          ...dot,
          background: isActive ? "#38bdf8" : "#64748b",
          animation: isActive ? "pulse 2s infinite" : "none",
        }}
      />

      <div>
        <div style={label}>Robot status</div>
        <div style={value}>{status}</div>
      </div>
    </div>
  );
}

const container = {
  display: "flex",
  alignItems: "center",
  gap: 12,
};

const dot = {
  width: 10,
  height: 10,
  borderRadius: "50%",
};

const label = {
  fontSize: 12,
  color: "#64748b",
};

const value = {
  fontWeight: 600,
};