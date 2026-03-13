import { apiRequest } from "../../lib/api/client";

export function getDashboardSummary(token) {
  return apiRequest("/analytics/dashboard", { token });
}

export function getStudyTimeSeries(token) {
  return apiRequest("/analytics/study-time-series", { token });
}

export function getSubjectDistribution(token) {
  return apiRequest("/analytics/subjects", { token });
}

export function getProductivityTrend(token) {
  return apiRequest("/analytics/productivity-trend", { token });
}

export function getRecentActivity(token) {
  return apiRequest("/analytics/recent-activity", { token });
}
