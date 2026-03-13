const BAR_COLOR = "#2563eb";
const W = 600;
const H = 160;
const PAD = { top: 16, right: 16, bottom: 40, left: 48 };

export function StudyTimeChart({ series }) {
  if (!series || series.length === 0) {
    return <div className="chart-empty">No study data yet.</div>;
  }

  const innerW = W - PAD.left - PAD.right;
  const innerH = H - PAD.top - PAD.bottom;
  const maxVal = Math.max(...series.map((d) => d.study_minutes), 1);
  const barW = Math.max(6, innerW / series.length - 4);

  return (
    <div className="chart-wrap">
      <svg viewBox={`0 0 ${W} ${H}`} style={{ width: "100%", height: "auto" }}>
        {/* Y-axis label */}
        <text x={12} y={PAD.top + innerH / 2} fontSize={10} fill="#64748b" textAnchor="middle"
          transform={`rotate(-90, 12, ${PAD.top + innerH / 2})`}>mins</text>

        {/* Bars */}
        {series.map((d, i) => {
          const barH = (d.study_minutes / maxVal) * innerH;
          const x = PAD.left + i * (innerW / series.length) + (innerW / series.length - barW) / 2;
          const y = PAD.top + innerH - barH;
          const label = d.date.slice(5); // MM-DD
          return (
            <g key={d.date}>
              <rect x={x} y={y} width={barW} height={Math.max(barH, 1)} fill={BAR_COLOR} rx={2} opacity={0.85} />
              <text x={x + barW / 2} y={H - PAD.bottom + 14} fontSize={9} fill="#64748b" textAnchor="middle">{label}</text>
              {d.study_minutes > 0 && (
                <text x={x + barW / 2} y={y - 3} fontSize={9} fill={BAR_COLOR} textAnchor="middle">{d.study_minutes}</text>
              )}
            </g>
          );
        })}

        {/* Baseline */}
        <line x1={PAD.left} y1={PAD.top + innerH} x2={W - PAD.right} y2={PAD.top + innerH} stroke="#e2e8f0" strokeWidth={1} />
      </svg>
    </div>
  );
}
