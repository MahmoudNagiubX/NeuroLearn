const W = 600;
const H = 180;
const PAD = { top: 16, right: 16, bottom: 40, left: 48 };
const METRICS = [
  { key: "study_minutes", color: "#2563eb", label: "Study (min)" },
  { key: "completed_tasks", color: "#16a34a", label: "Tasks" },
  { key: "pomodoro_sessions", color: "#dc2626", label: "Pomodoros" },
];
const GROUP_W_FRAC = 0.7; // fraction of slot used by group

export function ProductivityTrendChart({ trend }) {
  if (!trend || trend.length === 0) {
    return <div className="chart-empty">No productivity data yet.</div>;
  }

  const innerW = W - PAD.left - PAD.right;
  const innerH = H - PAD.top - PAD.bottom;
  const maxVal = Math.max(...trend.flatMap((d) => METRICS.map((m) => d[m.key])), 1);
  const slotW = innerW / trend.length;
  const barW = (slotW * GROUP_W_FRAC) / METRICS.length;

  return (
    <div className="chart-wrap">
      <svg viewBox={`0 0 ${W} ${H}`} style={{ width: "100%", height: "auto" }}>
        {trend.map((d, i) => {
          const slotX = PAD.left + i * slotW;
          const label = d.date.slice(5);
          return (
            <g key={d.date}>
              {METRICS.map((m, mi) => {
                const val = d[m.key];
                const barH = (val / maxVal) * innerH;
                const x = slotX + (slotW * (1 - GROUP_W_FRAC)) / 2 + mi * barW;
                const y = PAD.top + innerH - barH;
                return (
                  <rect key={m.key} x={x} y={y} width={barW - 1} height={Math.max(barH, 1)}
                    fill={m.color} rx={2} opacity={0.8} />
                );
              })}
              <text x={slotX + slotW / 2} y={H - PAD.bottom + 14} fontSize={9} fill="#64748b" textAnchor="middle">{label}</text>
            </g>
          );
        })}
        {/* Baseline */}
        <line x1={PAD.left} y1={PAD.top + innerH} x2={W - PAD.right} y2={PAD.top + innerH} stroke="#e2e8f0" strokeWidth={1} />

        {/* Legend */}
        {METRICS.map((m, i) => (
          <g key={m.key}>
            <rect x={PAD.left + i * 100} y={H - 12} width={10} height={10} fill={m.color} rx={2} />
            <text x={PAD.left + i * 100 + 14} y={H - 3} fontSize={9} fill="#64748b">{m.label}</text>
          </g>
        ))}
      </svg>
    </div>
  );
}
