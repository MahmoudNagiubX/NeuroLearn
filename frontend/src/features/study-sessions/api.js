import { apiRequest } from "../../lib/api/client";

export function listStudySessions(token, query) {
  return apiRequest("/study-sessions", { token, query });
}

export function createStudySession(token, payload) {
  return apiRequest("/study-sessions", { method: "POST", token, body: payload });
}

export function startStudySession(token, sessionId) {
  return apiRequest(`/study-sessions/${sessionId}/start`, { method: "POST", token });
}

export function completeStudySession(token, sessionId) {
  return apiRequest(`/study-sessions/${sessionId}/complete`, { method: "POST", token });
}

export function cancelStudySession(token, sessionId) {
  return apiRequest(`/study-sessions/${sessionId}/cancel`, { method: "POST", token });
}
