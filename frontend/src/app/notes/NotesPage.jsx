import { useEffect, useState } from "react";

import {
  createNote,
  createNoteAttachment,
  createNoteFolder,
  deleteNoteAttachment,
  listNoteAttachments,
  listNoteFolders,
  listNotes,
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
    if (!noteId) {
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
  }, [selectedNoteId]);

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
      await createNote(token, {
        title: noteTitle,
        content_md: noteContent,
        subject_id: noteSubjectId || null,
        folder_id: noteFolderId || null,
      });
      setNoteTitle("");
      setNoteContent("");
      setNoteSubjectId("");
      setNoteFolderId("");
      await loadBaseData();
    } catch (err) {
      setError(err.message);
    }
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
    <div className="grid-three">
      <section className="card">
        <h2>Folders</h2>
        <form className="stack" onSubmit={handleCreateFolder}>
          <label>
            Folder Name
            <input value={folderName} onChange={(e) => setFolderName(e.target.value)} required />
          </label>
          <button type="submit">Create Folder</button>
        </form>
        <ul className="list">
          {folders.map((folder) => (
            <li key={folder.id}>{folder.name}</li>
          ))}
          {!folders.length ? <li>No folders yet.</li> : null}
        </ul>
      </section>

      <section className="card">
        <h2>Notes</h2>
        <form className="stack" onSubmit={handleCreateNote}>
          <label>
            Title
            <input value={noteTitle} onChange={(e) => setNoteTitle(e.target.value)} required />
          </label>
          <label>
            Content (Markdown)
            <textarea value={noteContent} onChange={(e) => setNoteContent(e.target.value)} rows={4} required />
          </label>
          <label>
            Subject
            <select value={noteSubjectId} onChange={(e) => setNoteSubjectId(e.target.value)}>
              <option value="">No subject</option>
              {subjects.map((subject) => (
                <option key={subject.id} value={subject.id}>
                  {subject.name}
                </option>
              ))}
            </select>
          </label>
          <label>
            Folder
            <select value={noteFolderId} onChange={(e) => setNoteFolderId(e.target.value)}>
              <option value="">No folder</option>
              {folders.map((folder) => (
                <option key={folder.id} value={folder.id}>
                  {folder.name}
                </option>
              ))}
            </select>
          </label>
          <button type="submit">Create Note</button>
        </form>

        <ul className="list">
          {notes.map((note) => (
            <li key={note.id}>
              <div>
                <strong>{note.title}</strong>
                <span>{note.content_md.slice(0, 80)}</span>
              </div>
              <button type="button" onClick={() => setSelectedNoteId(note.id)}>
                Attachments
              </button>
            </li>
          ))}
          {!notes.length ? <li>No notes yet.</li> : null}
        </ul>
      </section>

      <section className="card">
        <h2>Attachments Metadata</h2>
        {selectedNoteId ? <p>Selected Note: {selectedNoteId}</p> : <p>Select a note first.</p>}
        <form className="stack" onSubmit={handleCreateAttachment}>
          <label>
            Original Filename
            <input
              value={attachmentFilename}
              onChange={(e) => setAttachmentFilename(e.target.value)}
              required
              disabled={!selectedNoteId}
            />
          </label>
          <label>
            Storage Key
            <input
              value={attachmentStorageKey}
              onChange={(e) => setAttachmentStorageKey(e.target.value)}
              required
              disabled={!selectedNoteId}
            />
          </label>
          <label>
            MIME Type
            <input
              value={attachmentMimeType}
              onChange={(e) => setAttachmentMimeType(e.target.value)}
              disabled={!selectedNoteId}
            />
          </label>
          <button type="submit" disabled={!selectedNoteId}>
            Add Attachment Metadata
          </button>
        </form>

        <ul className="list">
          {attachments.map((attachment) => (
            <li key={attachment.id}>
              <div>
                <strong>{attachment.original_filename}</strong>
                <span>{attachment.storage_key}</span>
              </div>
              <button type="button" onClick={() => handleDeleteAttachment(attachment.id)}>
                Delete
              </button>
            </li>
          ))}
          {selectedNoteId && !attachments.length ? <li>No attachments yet.</li> : null}
        </ul>

        {error ? <p className="error">{error}</p> : null}
      </section>
    </div>
  );
}
