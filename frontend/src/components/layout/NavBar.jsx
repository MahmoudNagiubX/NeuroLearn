import { Link, useLocation } from "react-router-dom";

import { useAuth } from "../../hooks/useAuth";

const NAV_ITEMS = [
  { to: "/", label: "Dashboard" },
  { to: "/subjects", label: "Subjects" },
  { to: "/tasks", label: "Tasks" },
  { to: "/study-sessions", label: "Study Sessions" },
  { to: "/pomodoro", label: "Pomodoro" },
  { to: "/notes", label: "Notes" },
];

export function NavBar() {
  const { pathname } = useLocation();
  const { user, logout } = useAuth();

  return (
    <header className="nav-shell">
      <div className="nav-left">
        <h1>NeuroLearn</h1>
        <p>Smoke Test UI</p>
      </div>
      <nav className="nav-links">
        {NAV_ITEMS.map((item) => (
          <Link key={item.to} to={item.to} className={pathname === item.to ? "active" : ""}>
            {item.label}
          </Link>
        ))}
      </nav>
      <div className="nav-right">
        <span>{user?.email}</span>
        <button type="button" onClick={logout}>
          Logout
        </button>
      </div>
    </header>
  );
}
