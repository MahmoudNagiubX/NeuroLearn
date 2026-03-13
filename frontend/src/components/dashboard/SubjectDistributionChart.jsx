const COLORS = ["#2563eb", "#16a34a", "#dc2626", "#9333ea", "#f59e0b", "#0891b2", "#db2777"];
const ROW_H = 32;
const BAR_MAX_W = 260;
const LABEL_W = 120;
const W = 480;

export function SubjectDistributionChart({ data }) {
  if (!data || data.length === 0) {
    return <div className="chart-empty">No subject study data yet.</div>;
  }

  const maxVal = Math.max(...data.map((d) => d.total_minutes), 1);
  const H = data.length * ROW_H + 16;

  return (
    <div className="chart-wrap">
      <svg viewBox={`0 0 ${W} ${H}`} style={{ width: "100%", height: "auto" }}>
        {data.map((d, i) => {
          const barW = (d.total_minutes / maxVal) * BAR_MAX_W;
          const y = i * ROW_H + 8;
          const color = COLORS[i % COLORS.length];
          const label = (d.subject_name || "Uncategorized").slice(0, 16);
          const mins = d.total_minutes;
          return (
            <g key={d.subject_id ?? i}>
              <text x={LABEL_W - 6} y={y + ROW_H / 2 + 4} fontSize={11} fill="#334155" textAnchor="end">{label}</text>
              <rect x={LABEL_W} y={y + 4} width={Math.max(barW, 2)} height={ROW_H - 10} fill={color} rx={3} opacity={0.82} />
              <text x={LABEL_W + Math.max(barW, 2) + 6} y={y + ROW_H / 2 + 4} fontSize={10} fill="#64748b">{mins}m</text>
            </g>
          );
        })}
      </svg>
    </div>
  );
}
