import { useEffect, useState } from "react";

import { createSubject, listSubjects } from "../../features/subjects/api";
import { useAuth } from "../../hooks/useAuth";

export function SubjectsPage() {
  const { token } = useAuth();

  const [subjects, setSubjects] = useState([]);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [error, setError] = useState("");

  async function loadSubjects() {
    if (!token) return;
    try {
      const data = await listSubjects(token);
      setSubjects(data);
    } catch (err) {
      setError(err.message);
    }
  }

  useEffect(() => {
    loadSubjects();
  }, [token]);

  async function handleCreate(event) {
    event.preventDefault();
    setError("");
    try {
      await createSubject(token, {
        name,
        description: description || null,
      });
      setName("");
      setDescription("");
      await loadSubjects();
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="grid-two">
      <section className="card">
        <h2>Create Subject</h2>
        <form onSubmit={handleCreate} className="stack">
          <label>
            Name
            <input value={name} onChange={(e) => setName(e.target.value)} required />
          </label>
          <label>
            Description
            <textarea value={description} onChange={(e) => setDescription(e.target.value)} rows={3} />
          </label>
          <button type="submit">Create Subject</button>
        </form>
        {error ? <p className="error">{error}</p> : null}
      </section>

      <section className="card">
        <h2>Subjects</h2>
        <ul className="list">
          {subjects.map((subject) => (
            <li key={subject.id}>
              <strong>{subject.name}</strong>
              <span>{subject.description || "No description"}</span>
            </li>
          ))}
          {!subjects.length ? <li>No subjects yet.</li> : null}
        </ul>
      </section>
    </div>
  );
}
