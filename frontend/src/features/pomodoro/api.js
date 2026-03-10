import { apiRequest } from "../../lib/api/client";

export function listPomodoroSessions(token, query) {
  return apiRequest("/pomodoro-sessions", { token, query });
}

export function createPomodoroSession(token, payload) {
  return apiRequest("/pomodoro-sessions", { method: "POST", token, body: payload });
}

export function completePomodoroSession(token, pomodoroId) {
  return apiRequest(`/pomodoro-sessions/${pomodoroId}/complete`, { method: "POST", token });
}
