import { useState, useEffect } from "react";
import { useAuth } from "../../hooks/useAuth";
import {
  getDashboardSummary,
  getStudyTimeSeries,
  getSubjectDistribution,
  getProductivityTrend,
  getRecentActivity,
} from "./api";

function useAnalyticsData(fetchFn) {
  const { token } = useAuth();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!token) return;
    let cancelled = false;
    setLoading(true);
    setError(null);
    fetchFn(token)
      .then((result) => {
        if (!cancelled) setData(result);
      })
      .catch((err) => {
        if (!cancelled) setError(err.message || "Failed to load data");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [token]);

  return { data, loading, error };
}

export function useDashboardAnalytics() {
  return useAnalyticsData(getDashboardSummary);
}

export function useStudyTimeSeries() {
  return useAnalyticsData(getStudyTimeSeries);
}

export function useSubjectDistribution() {
  return useAnalyticsData(getSubjectDistribution);
}

export function useProductivityTrend() {
  return useAnalyticsData(getProductivityTrend);
}

export function useRecentActivity() {
  return useAnalyticsData(getRecentActivity);
}
