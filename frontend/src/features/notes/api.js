import { apiRequest } from "../../lib/api/client";

export function listNoteFolders(token) {
  return apiRequest("/note-folders", { token });
}

export function createNoteFolder(token, payload) {
  return apiRequest("/note-folders", { method: "POST", token, body: payload });
}

export function listNotes(token, query) {
  return apiRequest("/notes", { token, query });
}

export function createNote(token, payload) {
  return apiRequest("/notes", { method: "POST", token, body: payload });
}

export function listNoteAttachments(token, noteId) {
  return apiRequest(`/notes/${noteId}/attachments`, { token });
}

export function createNoteAttachment(token, noteId, payload) {
  return apiRequest(`/notes/${noteId}/attachments`, {
    method: "POST",
    token,
    body: payload,
  });
}

export function deleteNoteAttachment(token, noteId, attachmentId) {
  return apiRequest(`/notes/${noteId}/attachments/${attachmentId}`, {
    method: "DELETE",
    token,
  });
}
