import { useEffect, useState } from "react";

import { listSubjects } from "../../features/subjects/api";
import { completeTask, createTask, createTaskList, listTaskLists, listTasks } from "../../features/tasks/api";
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

  return (
    <div className="grid-two">
      <section className="card">
        <h2>Create Task</h2>
        <form className="stack" onSubmit={handleCreateTask}>
          <label>
            Title
            <input value={taskTitle} onChange={(e) => setTaskTitle(e.target.value)} required />
          </label>
          <label>
            Description
            <textarea value={taskDescription} onChange={(e) => setTaskDescription(e.target.value)} rows={2} />
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
            Task List
            <select value={taskListId} onChange={(e) => setTaskListId(e.target.value)}>
              <option value="">No task list</option>
              {taskLists.map((taskList) => (
                <option key={taskList.id} value={taskList.id}>
                  {taskList.name}
                </option>
              ))}
            </select>
          </label>
          <button type="submit">Create Task</button>
        </form>

        <h3>Create Task List</h3>
        <form className="stack" onSubmit={handleCreateTaskList}>
          <label>
            Name
            <input value={taskListName} onChange={(e) => setTaskListName(e.target.value)} required />
          </label>
          <button type="submit">Create Task List</button>
        </form>

        {error ? <p className="error">{error}</p> : null}
      </section>

      <section className="card">
        <h2>Tasks</h2>
        <ul className="list">
          {tasks.map((task) => (
            <li key={task.id}>
              <div>
                <strong>{task.title}</strong>
                <span>Status: {task.status}</span>
              </div>
              {task.status !== "done" ? (
                <button type="button" onClick={() => handleCompleteTask(task.id)}>
                  Mark Complete
                </button>
              ) : null}
            </li>
          ))}
          {!tasks.length ? <li>No tasks yet.</li> : null}
        </ul>
      </section>
    </div>
  );
}
