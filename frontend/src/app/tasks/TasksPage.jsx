import { useEffect, useState } from "react";

import { listSubjects } from "../../features/subjects/api";
import {
  completeTask,
  createTask,
  createTaskList,
  listTaskLists,
  listTasks,
  updateTask,
} from "../../features/tasks/api";
import { useAuth } from "../../hooks/useAuth";

export function TasksPage() {
  const { token } = useAuth();

  const [tasks, setTasks] = useState([]);
  const [subjects, setSubjects] = useState([]);
  const [taskLists, setTaskLists] = useState([]);
  const [error, setError] = useState("");

  const [taskTitle, setTaskTitle] = useState("");
  const [taskDescription, setTaskDescription] = useState("");
  const [subjectId, setSubjectId] = useState("");
  const [taskListId, setTaskListId] = useState("");

  const [taskListName, setTaskListName] = useState("");

  async function loadPageData() {
    if (!token) return;
    try {
      const [tasksData, subjectsData, taskListsData] = await Promise.all([
        listTasks(token),
        listSubjects(token),
        listTaskLists(token),
      ]);
      setTasks(tasksData);
      setSubjects(subjectsData);
      setTaskLists(taskListsData);
    } catch (err) {
      setError(err.message);
    }
  }

  useEffect(() => {
    loadPageData();
  }, [token]);

  async function handleCreateTask(event) {
    event.preventDefault();
    setError("");
    try {
      await createTask(token, {
        title: taskTitle,
        description: taskDescription || null,
        subject_id: subjectId || null,
        task_list_id: taskListId || null,
      });
      setTaskTitle("");
      setTaskDescription("");
      setSubjectId("");
      setTaskListId("");
      await loadPageData();
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleCreateTaskList(event) {
    event.preventDefault();
    setError("");
    try {
      await createTaskList(token, { name: taskListName });
      setTaskListName("");
      await loadPageData();
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleCompleteTask(taskId) {
    setError("");
    try {
      await completeTask(token, taskId);
      await loadPageData();
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleStartTask(taskId) {
    setError("");
    try {
      await updateTask(token, taskId, { status: "in_progress" });
      await loadPageData();
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="grid-two">
      <div className="stack">
        <section className="card">
          <h2>Create Task</h2>
          <form className="stack" onSubmit={handleCreateTask}>
            <label>
              Title
              <input value={taskTitle} onChange={(e) => setTaskTitle(e.target.value)} placeholder="What needs to be done?" required />
            </label>
            <label>
              Description
              <textarea value={taskDescription} onChange={(e) => setTaskDescription(e.target.value)} placeholder="Add details..." rows={2} />
            </label>
            <div className="grid-two" style={{ gap: "0.5rem", marginBottom: "0.5rem" }}>
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
                Task List
                <select value={taskListId} onChange={(e) => setTaskListId(e.target.value)}>
                  <option value="">No list</option>
                  {taskLists.map((taskList) => (
                    <option key={taskList.id} value={taskList.id}>
                      {taskList.name}
                    </option>
                  ))}
                </select>
              </label>
            </div>
            <button type="submit">Add Task</button>
          </form>
          {error ? <p className="error">{error}</p> : null}
        </section>

        <section className="card">
          <h3>New Task List</h3>
          <p style={{ fontSize: "0.85rem", color: "#64748b", margin: "0 0 1rem 0" }}>Group tasks together for better focus.</p>
          <form className="stack" onSubmit={handleCreateTaskList}>
            <div style={{ display: "flex", gap: "0.5rem" }}>
              <input style={{ flex: 1 }} value={taskListName} onChange={(e) => setTaskListName(e.target.value)} placeholder="List name..." required />
              <button type="submit" className="secondary">Create</button>
            </div>
          </form>
        </section>
      </div>

      <section className="card">
        <h2>Your Tasks</h2>
        <ul className="list">
          {tasks.map((task) => (
            <li key={task.id} style={{ opacity: task.status === "done" ? 0.6 : 1 }}>
              <div>
                <strong style={{ textDecoration: task.status === "done" ? "line-through" : "none" }}>{task.title}</strong>
                <span style={{ fontSize: "0.85rem", color: "#64748b" }}>
                  {task.status === "done" ? "Completed" : task.status === "in_progress" ? "In Progress" : "To Do"}
                  {task.description ? ` • ${task.description.slice(0, 30)}${task.description.length > 30 ? "..." : ""}` : ""}
                </span>
              </div>
              <div className="row-actions">
                {task.status === "todo" ? (
                  <button type="button" className="secondary" onClick={() => handleStartTask(task.id)}>
                    Start
                  </button>
                ) : null}
                {task.status !== "done" ? (
                  <button type="button" onClick={() => handleCompleteTask(task.id)}>
                    ✓ Done
                  </button>
                ) : null}
              </div>
            </li>
          ))}
          {!tasks.length ? <li style={{ justifyContent: "center", color: "#94a3b8" }}>No tasks yet. Enjoy your day!</li> : null}
        </ul>
      </section>
    </div>
  );
}
