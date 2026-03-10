import { apiRequest } from "../../lib/api/client";

export function listSubjects(token) {
  return apiRequest("/subjects", { token });
}

export function createSubject(token, payload) {
  return apiRequest("/subjects", { method: "POST", token, body: payload });
}
