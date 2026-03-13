const EVENT_ICONS = {
  TASK_CREATED: "📝",
  TASK_COMPLETED: "✅",
  STUDY_SESSION_STARTED: "📖",
  STUDY_SESSION_COMPLETED: "🎓",
  POMODORO_STARTED: "🍅",
  POMODORO_COMPLETED: "🍅",
  NOTE_CREATED: "📄",
  SUBJECT_CREATED: "📚",
};

function formatEventLabel(eventType) {
  return eventType
    .split("_")
    .map((w) => w.charAt(0) + w.slice(1).toLowerCase())
    .join(" ");
}

function formatTime(isoString) {
  if (!isoString) return "";
  const d = new Date(isoString);
  return d.toLocaleString(undefined, {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function RecentActivityList({ activity }) {
  if (!activity || activity.length === 0) {
    return <div className="chart-empty">No recent activity yet.</div>;
  }

  return (
    <ul className="list activity-list">
      {activity.map((item, i) => (
        <li key={i}>
          <div>
            <strong>
              {EVENT_ICONS[item.event_type] || "⚡"} {formatEventLabel(item.event_type)}
            </strong>
            {item.entity_type && (
              <span className="activity-entity">{item.entity_type}</span>
            )}
          </div>
          <span className="activity-time">{formatTime(item.occurred_at)}</span>
        </li>
      ))}
    </ul>
  );
}
