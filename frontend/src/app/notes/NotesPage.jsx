import { useEffect, useState } from "react";

import {
  createNote,
  createNoteAttachment,
  createNoteFolder,
  deleteNoteAttachment,
  listNoteAttachments,
  listNoteFolders,
  listNotes,
  updateNote,
} from "../../features/notes/api";
import { listSubjects } from "../../features/subjects/api";
import { useAuth } from "../../hooks/useAuth";

export function NotesPage() {
  const { token } = useAuth();

  const [subjects, setSubjects] = useState([]);
  const [folders, setFolders] = useState([]);
  const [notes, setNotes] = useState([]);
  const [attachments, setAttachments] = useState([]);

  const [selectedNoteId, setSelectedNoteId] = useState("");
  const [editingNoteId, setEditingNoteId] = useState("");
  const [error, setError] = useState("");

  const [folderName, setFolderName] = useState("");

  const [noteTitle, setNoteTitle] = useState("");
  const [noteContent, setNoteContent] = useState("");
  const [noteSubjectId, setNoteSubjectId] = useState("");
  const [noteFolderId, setNoteFolderId] = useState("");

  const [attachmentFilename, setAttachmentFilename] = useState("");
  const [attachmentStorageKey, setAttachmentStorageKey] = useState("");
  const [attachmentMimeType, setAttachmentMimeType] = useState("");

  async function loadBaseData() {
    if (!token) return;
    try {
      const [subjectsData, foldersData, notesData] = await Promise.all([
        listSubjects(token),
        listNoteFolders(token),
        listNotes(token),
      ]);
      setSubjects(subjectsData);
      setFolders(foldersData);
      setNotes(notesData);
      if (selectedNoteId && !notesData.find((note) => note.id === selectedNoteId)) {
        setSelectedNoteId("");
        setAttachments([]);
      }
    } catch (err) {
      setError(err.message);
    }
  }

  async function loadAttachments(noteId) {
    if (!noteId || !token) {
      setAttachments([]);
      return;
    }
    try {
      const data = await listNoteAttachments(token, noteId);
      setAttachments(data);
    } catch (err) {
      setError(err.message);
    }
  }

  useEffect(() => {
    loadBaseData();
  }, [token]);

  useEffect(() => {
    loadAttachments(selectedNoteId);
  }, [selectedNoteId, token]);

  async function handleCreateFolder(event) {
    event.preventDefault();
    setError("");
    try {
      await createNoteFolder(token, { name: folderName, parent_id: null });
      setFolderName("");
      await loadBaseData();
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleCreateNote(event) {
    event.preventDefault();
    setError("");
    try {
      const payload = {
        title: noteTitle,
        content_md: noteContent,
        subject_id: noteSubjectId || null,
        folder_id: noteFolderId || null,
      };

      if (editingNoteId) {
        await updateNote(token, editingNoteId, payload);
      } else {
        await createNote(token, payload);
      }

      setNoteTitle("");
      setNoteContent("");
      setNoteSubjectId("");
      setNoteFolderId("");
      setEditingNoteId("");
      await loadBaseData();
    } catch (err) {
      setError(err.message);
    }
  }

  function handleEditNote(note) {
    setEditingNoteId(note.id);
    setNoteTitle(note.title);
    setNoteContent(note.content_md);
    setNoteSubjectId(note.subject_id || "");
    setNoteFolderId(note.folder_id || "");
    setError("");
  }

  function handleCancelEdit() {
    setEditingNoteId("");
    setNoteTitle("");
    setNoteContent("");
    setNoteSubjectId("");
    setNoteFolderId("");
  }

  async function handleCreateAttachment(event) {
    event.preventDefault();
    if (!selectedNoteId) return;
    setError("");
    try {
      await createNoteAttachment(token, selectedNoteId, {
        original_filename: attachmentFilename,
        storage_key: attachmentStorageKey,
        mime_type: attachmentMimeType || null,
      });
      setAttachmentFilename("");
      setAttachmentStorageKey("");
      setAttachmentMimeType("");
      await loadAttachments(selectedNoteId);
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleDeleteAttachment(attachmentId) {
    if (!selectedNoteId) return;
    setError("");
    try {
      await deleteNoteAttachment(token, selectedNoteId, attachmentId);
      await loadAttachments(selectedNoteId);
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="grid-two">
      <div className="stack">
        <section className="card mb-4" style={{ padding: "0.5rem" }}>
          <form className="stack" onSubmit={handleCreateNote}>
            <input
              value={noteTitle}
              onChange={(e) => setNoteTitle(e.target.value)}
              placeholder="Title"
              style={{ fontWeight: "bold", border: "none", fontSize: "1.1rem", padding: "0.5rem 1rem" }}
              required
            />
            <textarea
              value={noteContent}
              onChange={(e) => setNoteContent(e.target.value)}
              placeholder="Take a note..."
              rows={4}
              style={{ border: "none", resize: "none", padding: "0 1rem" }}
              required
            />
            <div className="grid-two" style={{ gap: "0.5rem", padding: "0.5rem 1rem" }}>
              <select value={noteSubjectId} onChange={(e) => setNoteSubjectId(e.target.value)} style={{ background: "#f8fafc", border: "none" }}>
                <option value="">No subject</option>
                {subjects.map((subject) => (
                  <option key={subject.id} value={subject.id}>{subject.name}</option>
                ))}
              </select>
              <select value={noteFolderId} onChange={(e) => setNoteFolderId(e.target.value)} style={{ background: "#f8fafc", border: "none" }}>
                <option value="">No folder</option>
                {folders.map((folder) => (
                  <option key={folder.id} value={folder.id}>{folder.name}</option>
                ))}
              </select>
            </div>
            <div style={{ display: "flex", gap: "0.5rem", justifyContent: "flex-end", padding: "0.5rem 1rem" }}>
              {editingNoteId ? (
                <button type="button" className="secondary" onClick={handleCancelEdit}>Cancel</button>
              ) : null}
              <button type="submit">{editingNoteId ? "Save Note" : "Done"}</button>
            </div>
          </form>
        </section>

        <section className="card">
          <h3 style={{ marginTop: 0 }}>Folders</h3>
          <form style={{ display: "flex", gap: "0.5rem", marginBottom: "1rem" }} onSubmit={handleCreateFolder}>
            <input style={{ flex: 1 }} value={folderName} onChange={(e) => setFolderName(e.target.value)} placeholder="New folder..." required />
            <button type="submit" className="secondary">Add</button>
          </form>
          <div style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem" }}>
            {folders.map((folder) => (
              <span key={folder.id} style={{ background: "#f1f5f9", padding: "0.4rem 0.8rem", borderRadius: "999px", fontSize: "0.85rem", color: "#475569", display: "flex", alignItems: "center", gap: "0.4rem" }}>
                📁 {folder.name}
              </span>
            ))}
            {!folders.length ? <span style={{ color: "#94a3b8", fontSize: "0.85rem" }}>No folders yet.</span> : null}
          </div>
        </section>
      </div>

      <div className="stack">
        <section style={{ background: "transparent", border: "none", padding: 0 }}>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(240px, 1fr))", gap: "1rem" }}>
            {notes.map((note) => (
              <div key={note.id} className="card" style={{ display: "flex", flexDirection: "column", gap: "0.5rem", padding: "1.25rem" }}>
                <strong style={{ fontSize: "1.1rem" }}>{note.title}</strong>
                <p style={{ margin: 0, color: "#475569", fontSize: "0.95rem", whiteSpace: "pre-wrap" }}>
                  {note.content_md}
                </p>
                <div style={{ marginTop: "auto", paddingTop: "1rem", display: "flex", gap: "0.5rem" }}>
                  <button type="button" className="secondary" style={{ flex: 1, padding: "0.35rem" }} onClick={() => handleEditNote(note)}>Edit</button>
                  <button type="button" className="secondary" style={{ flex: 1, padding: "0.35rem" }} onClick={() => setSelectedNoteId(note.id)}>Attach</button>
                </div>
              </div>
            ))}
            {!notes.length ? <p style={{ color: "#94a3b8" }}>No notes yet. Create one on the left!</p> : null}
          </div>
        </section>

        {selectedNoteId && (
          <section className="card" style={{ marginTop: "1rem", background: "#f8fafc", borderColor: "#cbd5e1" }}>
            <h3 style={{ marginTop: 0 }}>Attachments Metadata</h3>
            <p style={{ fontSize: "0.85rem", color: "#64748b", margin: "0 0 1rem 0" }}>Manage file links for the selected note.</p>
            <form className="stack" onSubmit={handleCreateAttachment}>
              <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
                <input style={{ flex: 1, minWidth: "120px" }} value={attachmentFilename} onChange={(e) => setAttachmentFilename(e.target.value)} placeholder="File name" required />
                <input style={{ flex: 1, minWidth: "120px" }} value={attachmentStorageKey} onChange={(e) => setAttachmentStorageKey(e.target.value)} placeholder="Mock URL / Key" required />
                <button type="submit" className="secondary">Add</button>
              </div>
            </form>
            <ul className="list" style={{ marginTop: "1rem" }}>
              {attachments.map((attachment) => (
                <li key={attachment.id} style={{ padding: "0.5rem 0.75rem", border: "none", background: "#fff" }}>
                  <span style={{ fontSize: "0.9rem", color: "#334155" }}>📎 {attachment.original_filename}</span>
                  <button type="button" className="secondary" style={{ padding: "0.2rem 0.5rem", fontSize: "0.8rem", background: "transparent", border: "none", color: "#ef4444" }} onClick={() => handleDeleteAttachment(attachment.id)}>Remove</button>
                </li>
              ))}
              {!attachments.length ? <li style={{ color: "#94a3b8", fontSize: "0.85rem", justifyContent: "center", border: "none", background: "transparent" }}>No attachments found.</li> : null}
            </ul>
          </section>
        )}
      </div>
      {error && <div style={{ position: "fixed", bottom: "1rem", right: "1rem", background: "#fee2e2", color: "#b91c1c", padding: "1rem", borderRadius: "0.5rem", boxShadow: "0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -2px rgba(0,0,0,0.1)", zIndex: 50 }}>{error}</div>}
    </div>
  );
}
