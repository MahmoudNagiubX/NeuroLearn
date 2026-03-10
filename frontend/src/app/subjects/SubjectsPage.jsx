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
      <div className="stack">
        <section className="card">
          <h2>Create Subject</h2>
          <form className="stack" onSubmit={handleCreate}>
            <label>
              Name
              <input value={name} onChange={(e) => setName(e.target.value)} placeholder="e.g. Mathematics" required />
            </label>
            <label>
              Description
              <textarea value={description} onChange={(e) => setDescription(e.target.value)} placeholder="Optional details..." rows={2} />
            </label>
            <button type="submit">Create Subject</button>
          </form>
          {error ? <p className="error">{error}</p> : null}
        </section>
      </div>

      <section className="card">
        <h2>Your Subjects</h2>
        <ul className="list">
          {subjects.map((subject) => (
            <li key={subject.id}>
              <div>
                <strong style={{ fontSize: "1.05rem" }}>{subject.name}</strong>
                <span style={{ fontSize: "0.9rem", color: "#64748b" }}>{subject.description || "No description"}</span>
              </div>
            </li>
          ))}
          {!subjects.length ? <li style={{ justifyContent: "center", color: "#94a3b8" }}>No subjects yet.</li> : null}
        </ul>
      </section>
    </div>
  );
}
