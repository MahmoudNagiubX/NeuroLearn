import { Link } from "react-router-dom";

import { useAuth } from "../../hooks/useAuth";
import { useDashboardAnalytics } from "../../features/analytics/hooks";
import { DashboardStatsCards } from "../../components/dashboard/DashboardStatsCards";
import { StudyTimeChart } from "../../components/dashboard/StudyTimeChart";
import { SubjectDistributionChart } from "../../components/dashboard/SubjectDistributionChart";
import { ProductivityTrendChart } from "../../components/dashboard/ProductivityTrendChart";
import { RecentActivityList } from "../../components/dashboard/RecentActivityList";

export function DashboardPage() {
  const { user } = useAuth();
  const { data: summary, loading, error } = useDashboardAnalytics();

  return (
    <div className="page-shell dashboard-page">
      <div className="dashboard-header">
        <div>
          <h2 style={{ margin: 0 }}>Dashboard</h2>
          <p style={{ margin: "4px 0 0", color: "#64748b", fontSize: "0.9rem" }}>
            Welcome back, <strong>{user?.email}</strong>
          </p>
        </div>
        <div className="quick-links">
          <Link to="/subjects">Subjects</Link>
          <Link to="/tasks">Tasks</Link>
          <Link to="/study-sessions">Study Sessions</Link>
          <Link to="/pomodoro">Pomodoro</Link>
          <Link to="/notes">Notes</Link>
        </div>
      </div>

      {loading && <p className="dashboard-status">Loading analytics…</p>}
      {error && <p className="error">Failed to load analytics: {error}</p>}

      {summary && (
        <>
          {/* Stats row */}
          <DashboardStatsCards summary={summary} />

          {/* Study time chart */}
          <section className="card dashboard-section">
            <h3>Study Time History</h3>
            <StudyTimeChart series={summary.study_time_series} />
          </section>

          {/* Middle row: subject distribution + productivity trend */}
          <div className="grid-two">
            <section className="card dashboard-section">
              <h3>Subject Distribution</h3>
              <SubjectDistributionChart data={summary.subject_distribution} />
            </section>

            <section className="card dashboard-section">
              <h3>Productivity Trend (7 days)</h3>
              <ProductivityTrendChart trend={summary.productivity_trend} />
            </section>
          </div>

          {/* Recent activity */}
          <section className="card dashboard-section">
            <h3>Recent Activity</h3>
            <RecentActivityList activity={summary.recent_activity} />
          </section>
        </>
      )}
    </div>
  );
}
