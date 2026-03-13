function formatMinutes(minutes) {
  if (!minutes) return "0m";
  const h = Math.floor(minutes / 60);
  const m = minutes % 60;
  return h > 0 ? `${h}h ${m}m` : `${m}m`;
}

export function DashboardStatsCards({ summary }) {
  const stats = [
    {
      label: "Total Study Time",
      value: formatMinutes(summary.total_study_minutes),
      sub: `${formatMinutes(summary.weekly_study_minutes)} this week`,
      color: "#2563eb",
    },
    {
      label: "Completed Tasks",
      value: summary.completed_tasks,
      sub: `${summary.task_completion_rate}% completion rate`,
      color: "#16a34a",
    },
    {
      label: "Pomodoro Sessions",
      value: summary.pomodoro_sessions,
      sub: "completed",
      color: "#dc2626",
    },
    {
      label: "Notes Created",
      value: summary.notes_created,
      sub: `across ${summary.subjects_studied} subjects`,
      color: "#9333ea",
    },
  ];

  return (
    <div className="stats-grid">
      {stats.map((s) => (
        <div key={s.label} className="stat-card" style={{ borderTop: `4px solid ${s.color}` }}>
          <div className="stat-label">{s.label}</div>
          <div className="stat-value" style={{ color: s.color }}>{s.value}</div>
          <div className="stat-sub">{s.sub}</div>
        </div>
      ))}
    </div>
  );
}
