import { Link } from "react-router-dom";

import { useAuth } from "../../hooks/useAuth";

export function DashboardPage() {
  const { user } = useAuth();

  return (
    <section className="card">
      <h2>Dashboard</h2>
      <p>Signed in as: {user?.email}</p>
      <p>Use these quick links to smoke-test the backend slices:</p>
      <div className="quick-links">
        <Link to="/subjects">Subjects</Link>
        <Link to="/tasks">Tasks</Link>
        <Link to="/study-sessions">Study Sessions</Link>
        <Link to="/pomodoro">Pomodoro</Link>
        <Link to="/notes">Notes</Link>
      </div>
    </section>
  );
}
