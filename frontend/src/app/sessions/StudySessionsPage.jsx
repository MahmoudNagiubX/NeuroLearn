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
      <section className="card">
        <h2>Create Study Session</h2>
        <form className="stack" onSubmit={handleCreate}>
          <label>
            Title
            <input value={title} onChange={(e) => setTitle(e.target.value)} />
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
              {filteredTasks.map((task) => (
                <option key={task.id} value={task.id}>
                  {task.title}
                </option>
              ))}
            </select>
          </label>
          <label>
            Scheduled Start
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
            Scheduled End
            <input
              type="datetime-local"
              value={scheduledEnd}
              onChange={(e) => setScheduledEnd(e.target.value)}
              required
            />
          </label>
          <button type="submit">Create Session</button>
        </form>
        {error ? <p className="error">{error}</p> : null}
      </section>

      <section className="card">
        <h2>Study Sessions</h2>
        <ul className="list">
          {studySessions.map((studySession) => (
            <li key={studySession.id}>
              <div>
                <strong>{studySession.title || "Untitled Session"}</strong>
                <span>Status: {studySession.status}</span>
              </div>
              <div className="row-actions">
                <button
                  type="button"
                  onClick={() => handleAction("start", studySession.id)}
                  disabled={studySession.status !== "scheduled"}
                >
                  Start
                </button>
                <button
                  type="button"
                  onClick={() => handleAction("complete", studySession.id)}
                  disabled={!["scheduled", "in_progress"].includes(studySession.status)}
                >
                  Complete
                </button>
                <button
                  type="button"
                  onClick={() => handleAction("cancel", studySession.id)}
                  disabled={!["scheduled", "in_progress"].includes(studySession.status)}
                >
                  Cancel
                </button>
              </div>
            </li>
          ))}
          {!studySessions.length ? <li>No study sessions yet.</li> : null}
        </ul>
      </section>
    </div>
  );
}
