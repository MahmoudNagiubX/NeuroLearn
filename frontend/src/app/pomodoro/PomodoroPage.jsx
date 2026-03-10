import { useEffect, useMemo, useState } from "react";

import { completePomodoroSession, createPomodoroSession, listPomodoroSessions } from "../../features/pomodoro/api";
import { listStudySessions } from "../../features/study-sessions/api";
import { listSubjects } from "../../features/subjects/api";
import { listTasks } from "../../features/tasks/api";
import { useAuth } from "../../hooks/useAuth";

export function PomodoroPage() {
  const { token } = useAuth();

  const [pomodoroSessions, setPomodoroSessions] = useState([]);
  const [subjects, setSubjects] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [studySessions, setStudySessions] = useState([]);
  const [error, setError] = useState("");

  const [plannedMinutes, setPlannedMinutes] = useState(25);
  const [sessionType, setSessionType] = useState("focus");
  const [subjectId, setSubjectId] = useState("");
  const [taskId, setTaskId] = useState("");
  const [studySessionId, setStudySessionId] = useState("");
  const [statusValue, setStatusValue] = useState("aborted");
  const filteredTasks = useMemo(
    () => (subjectId ? tasks.filter((task) => task.subject_id === subjectId) : tasks),
    [subjectId, tasks],
  );
  const filteredStudySessions = useMemo(
    () =>
      studySessions.filter((studySession) => {
        if (subjectId && studySession.subject_id && studySession.subject_id !== subjectId) {
          return false;
        }
        if (taskId && studySession.task_id && studySession.task_id !== taskId) {
          return false;
        }
        return true;
      }),
    [studySessions, subjectId, taskId],
  );

  async function loadData() {
    if (!token) return;
    try {
      const [pomodoroData, subjectsData, tasksData, sessionsData] = await Promise.all([
        listPomodoroSessions(token),
        listSubjects(token),
        listTasks(token),
        listStudySessions(token),
      ]);
      setPomodoroSessions(pomodoroData);
      setSubjects(subjectsData);
      setTasks(tasksData);
      setStudySessions(sessionsData);
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

  useEffect(() => {
    if (studySessionId && !filteredStudySessions.some((studySession) => studySession.id === studySessionId)) {
      setStudySessionId("");
    }
  }, [filteredStudySessions, studySessionId]);

  async function handleCreate(event) {
    event.preventDefault();
    setError("");
    try {
      await createPomodoroSession(token, {
        planned_minutes: Number(plannedMinutes),
        session_type: sessionType,
        subject_id: subjectId || null,
        task_id: taskId || null,
        study_session_id: studySessionId || null,
        status: statusValue,
      });
      setTaskId("");
      setStudySessionId("");
      await loadData();
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleComplete(id) {
    setError("");
    try {
      await completePomodoroSession(token, id);
      await loadData();
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="grid-two">
      <div className="stack">
        <section className="card">
          <h2>Log Pomodoro Session</h2>
          <p style={{ fontSize: "0.85rem", color: "#64748b", margin: "0 0 1rem 0" }}>Record a focus or break session.</p>
          <form className="stack" onSubmit={handleCreate}>
            <div className="grid-two" style={{ gap: "0.5rem" }}>
              <label>
                Duration (min)
                <input
                  type="number"
                  min={1}
                  value={plannedMinutes}
                  onChange={(e) => setPlannedMinutes(e.target.value)}
                  required
                />
              </label>
              <label>
                Type
                <select value={sessionType} onChange={(e) => setSessionType(e.target.value)}>
                  <option value="focus">Focus</option>
                  <option value="short_break">Short Break</option>
                  <option value="long_break">Long Break</option>
                </select>
              </label>
            </div>

            <div style={{ padding: "0.5rem 0" }}>
              <span style={{ display: "block", fontSize: "0.9rem", fontWeight: 600, marginBottom: "0.5rem" }}>Status</span>
              <div style={{ display: "flex", gap: "1rem" }}>
                <label style={{ flexDirection: "row", alignItems: "center", gap: "0.25rem", fontWeight: "normal" }}>
                  <input type="radio" value="completed" checked={statusValue === "completed"} onChange={(e) => setStatusValue(e.target.value)} />
                  Completed
                </label>
                <label style={{ flexDirection: "row", alignItems: "center", gap: "0.25rem", fontWeight: "normal" }}>
                  <input type="radio" value="aborted" checked={statusValue === "aborted"} onChange={(e) => setStatusValue(e.target.value)} />
                  Aborted
                </label>
              </div>
            </div>

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
            <label>
              Study Session
              <select value={studySessionId} onChange={(e) => setStudySessionId(e.target.value)}>
                <option value="">No study session</option>
                {filteredStudySessions.map((studySession) => (
                  <option key={studySession.id} value={studySession.id}>
                    {studySession.title || `Session ${studySession.id.slice(0, 8)}`}
                  </option>
                ))}
              </select>
            </label>
            <button type="submit">Log Session</button>
          </form>
          {error ? <p className="error">{error}</p> : null}
        </section>
      </div>

      <section className="card">
        <h2>Recent Sessions</h2>
        <ul className="list">
          {pomodoroSessions.map((pomodoroSession) => (
            <li key={pomodoroSession.id} style={{ opacity: pomodoroSession.status === "aborted" ? 0.6 : 1 }}>
              <div>
                <strong style={{ textTransform: "capitalize" }}>{pomodoroSession.session_type.replace("_", " ")}</strong>
                <span style={{ fontSize: "0.85rem", color: "#64748b" }}>
                  {pomodoroSession.planned_minutes} min • {pomodoroSession.status === "completed" ? "✅ Completed" : "❌ Aborted"}
                </span>
              </div>
              {pomodoroSession.status !== "completed" && pomodoroSession.status !== "aborted" ? (
                <button type="button" onClick={() => handleComplete(pomodoroSession.id)}>
                  Complete
                </button>
              ) : null}
            </li>
          ))}
          {!pomodoroSessions.length ? <li style={{ justifyContent: "center", color: "#94a3b8" }}>No sessions yet. Time to focus!</li> : null}
        </ul>
      </section>
    </div>
  );
}
