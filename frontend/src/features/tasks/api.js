import { apiRequest } from "../../lib/api/client";

export function listTasks(token, query) {
  return apiRequest("/tasks", { token, query });
}

export function createTask(token, payload) {
  return apiRequest("/tasks", { method: "POST", token, body: payload });
}

export function completeTask(token, taskId) {
  return apiRequest(`/tasks/${taskId}/complete`, { method: "POST", token });
}

export function listTaskLists(token) {
  return apiRequest("/task-lists", { token });
}

export function createTaskList(token, payload) {
  return apiRequest("/task-lists", { method: "POST", token, body: payload });
}
