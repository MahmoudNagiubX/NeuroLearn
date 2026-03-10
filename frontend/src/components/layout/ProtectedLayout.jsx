import { Navigate, Outlet } from "react-router-dom";

import { useAuth } from "../../hooks/useAuth";
import { NavBar } from "./NavBar";

export function ProtectedLayout() {
  const { token, loading } = useAuth();

  if (loading) {
    return <div className="page-shell">Loading...</div>;
  }

  if (!token) {
    return <Navigate to="/login" replace />;
  }

  return (
    <div className="app-shell">
      <NavBar />
      <main className="page-shell">
        <Outlet />
      </main>
    </div>
  );
}
