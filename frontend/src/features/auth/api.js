import { apiRequest } from "../../lib/api/client";

export function signup(payload) {
  return apiRequest("/auth/signup", { method: "POST", body: payload });
}

export function login(payload) {
  return apiRequest("/auth/login", { method: "POST", body: payload });
}

export function fetchCurrentUser(token) {
  return apiRequest("/auth/me", { token });
}
