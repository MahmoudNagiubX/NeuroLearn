import { useEffect, useMemo, useState } from "react";

import { listSubjects } from "../../features/subjects/api";
import {
  cancelStudySession,
  completeStudySession,
  createStudySession,
  listStudySessions,
  startStudySession,
} from "../../features/study-sessions/api";
import { listTasks } from "../../features/tasks/api";
import { useAuth } from "../../hooks/useAuth";

function toIso(localDateTimeValue) {
  return new Date(localDateTimeValue).toISOString();
}

function defaultEnd(startInput) {
  const startDate = new Date(startInput);
  startDate.setHours(startDate.getHours() + 1);
  return startDate.toISOString().slice(0, 16);
}

export function StudySessionsPage() {
  const { token } = useAuth();

  const nowLocal = useMemo(() => new Date().toISOString().slice(0, 16), []);
  const [scheduledStart, setScheduledStart] = useState(nowLocal);
  const [scheduledEnd, setScheduledEnd] = useState(defaultEnd(nowLocal));

  const [title, setTitle] = useState("");
  const [subjectId, setSubjectId] = useState("");
  const [taskId, setTaskId] = useState("");

  const [studySessions, setStudySessions] = useState([]);
  const [subjects, setSubjects] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [error, setError] = useState("");
  const filteredTasks = useMemo(
    () => (subjectId ? tasks.filter((task) => task.subject_id === subjectId) : tasks),
    [subjectId, tasks],
  );

  async function loadData() {
    if (!token) return;
    try {
      const [sessionsData, subjectsData, tasksData] = await Promise.all([
        listStudySessions(token),
        listSubjects(token),
        listTasks(token),
      ]);
      setStudySessions(sessionsData);
      setSubjects(subjectsData);
      setTasks(tasksData);
    } catch (err) {
      setError(err.message);
    }
  }

  useEffect(() => {
    loadData();
  }, [token]);

  useEffect(() => {
    if (taskId && !filteredTasks.some((task) => task.id === taskId)) {
      setTaskId("");
    }
  }, [filteredTasks, taskId]);

  async function handleCreate(event) {
    event.preventDefault();
    setError("");
    try {
      await createStudySession(token, {
        title: title || null,
        subject_id: subjectId || null,
        task_id: taskId || null,
        scheduled_start: toIso(scheduledStart),
        scheduled_end: toIso(scheduledEnd),
      });
      setTitle("");
      setSubjectId("");
      setTaskId("");
      await loadData();
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleAction(action, id) {
    setError("");
    try {
      if (action === "start") await startStudySession(token, id);
      if (action === "complete") await completeStudySession(token, id);
      if (action === "cancel") await cancelStudySession(token, id);
      await loadData();
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="grid-two">
      <div className="stack">
        <section className="card">
          <h2>Schedule Study Session</h2>
          <form className="stack" onSubmit={handleCreate}>
            <label>
              Title
              <input value={title} onChange={(e) => setTitle(e.target.value)} placeholder="e.g. Midterm Prep" />
            </label>
            <div className="grid-two" style={{ gap: "0.5rem" }}>
              <label>
                Subject
                <select value={subjectId} onChange={(e) => setSubjectId(e.target.value)}>
                  <option value="">No subject</option>
                  {subjects.map((subject) => (
                    <option key={subject.id} value={subject.id}>
                      {subject.name}
                    </option>
                  ))}
                </select>
              </label>
              <label>
                Task
                <select value={taskId} onChange={(e) => setTaskId(e.target.value)}>
                  <option value="">No task</option>
                  {filteredTasks.map((task) => (
                    <option key={task.id} value={task.id}>
                      {task.title}
                    </option>
                  ))}
                </select>
              </label>
            </div>

            <div className="grid-two" style={{ gap: "0.5rem" }}>
              <label>
                Start Time
                <input
                  type="datetime-local"
                  value={scheduledStart}
                  onChange={(e) => {
                    setScheduledStart(e.target.value);
                    if (scheduledEnd <= e.target.value) {
                      setScheduledEnd(defaultEnd(e.target.value));
                    }
                  }}
                  required
                />
              </label>
              <label>
                End Time
                <input
                  type="datetime-local"
                  value={scheduledEnd}
                  onChange={(e) => setScheduledEnd(e.target.value)}
                  required
                />
              </label>
            </div>
            <button type="submit">Schedule Session</button>
          </form>
          {error ? <p className="error">{error}</p> : null}
        </section>
      </div>

      <section className="card">
        <h2>Your Sessions</h2>
        <ul className="list">
          {studySessions.map((studySession) => (
            <li key={studySession.id} style={{ opacity: studySession.status === "cancelled" ? 0.6 : 1 }}>
              <div>
                <strong>{studySession.title || "Untitled Session"}</strong>
                <span style={{ fontSize: "0.85rem", color: "#64748b" }}>
                  {new Date(studySession.scheduled_start).toLocaleString(undefined, { month: "short", day: "numeric", hour: "numeric", minute: "2-digit" })}
                  {" — "}
                  {studySession.status === "scheduled" ? "📅 Scheduled" :
                    studySession.status === "in_progress" ? "⏳ In Progress" :
                      studySession.status === "completed" ? "✅ Completed" : "❌ Cancelled"}
                </span>
              </div>
              <div className="row-actions">
                {studySession.status === "scheduled" && (
                  <button type="button" className="secondary" onClick={() => handleAction("start", studySession.id)}>
                    Start
                  </button>
                )}
                {["scheduled", "in_progress"].includes(studySession.status) && (
                  <button type="button" onClick={() => handleAction("complete", studySession.id)}>
                    ✓ Done
                  </button>
                )}
                {["scheduled", "in_progress"].includes(studySession.status) && (
                  <button type="button" className="secondary" style={{ color: "#ef4444" }} onClick={() => handleAction("cancel", studySession.id)}>
                    Cancel
                  </button>
                )}
              </div>
            </li>
          ))}
          {!studySessions.length ? <li style={{ justifyContent: "center", color: "#94a3b8" }}>No study sessions planned.</li> : null}
        </ul>
      </section>
    </div>
  );
}
