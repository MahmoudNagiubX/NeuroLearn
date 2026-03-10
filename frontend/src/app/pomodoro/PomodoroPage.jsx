import { useEffect, useState } from "react";

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
      <section className="card">
        <h2>Create Pomodoro Session</h2>
        <form className="stack" onSubmit={handleCreate}>
          <label>
            Planned Minutes
            <input
              type="number"
              min={1}
              value={plannedMinutes}
              onChange={(e) => setPlannedMinutes(e.target.value)}
              required
            />
          </label>
          <label>
            Session Type
            <select value={sessionType} onChange={(e) => setSessionType(e.target.value)}>
              <option value="focus">focus</option>
              <option value="short_break">short_break</option>
              <option value="long_break">long_break</option>
            </select>
          </label>
          <label>
            Status
            <select value={statusValue} onChange={(e) => setStatusValue(e.target.value)}>
              <option value="aborted">aborted</option>
              <option value="completed">completed</option>
            </select>
          </label>
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
              {tasks.map((task) => (
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
              {studySessions.map((studySession) => (
                <option key={studySession.id} value={studySession.id}>
                  {studySession.title || studySession.id}
                </option>
              ))}
            </select>
          </label>
          <button type="submit">Create Pomodoro Session</button>
        </form>
        {error ? <p className="error">{error}</p> : null}
      </section>

      <section className="card">
        <h2>Pomodoro Sessions</h2>
        <ul className="list">
          {pomodoroSessions.map((pomodoroSession) => (
            <li key={pomodoroSession.id}>
              <div>
                <strong>{pomodoroSession.session_type}</strong>
                <span>
                  {pomodoroSession.status} | {pomodoroSession.planned_minutes} min
                </span>
              </div>
              {pomodoroSession.status !== "completed" ? (
                <button type="button" onClick={() => handleComplete(pomodoroSession.id)}>
                  Complete
                </button>
              ) : null}
            </li>
          ))}
          {!pomodoroSessions.length ? <li>No pomodoro sessions yet.</li> : null}
        </ul>
      </section>
    </div>
  );
}
