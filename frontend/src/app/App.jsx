import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";

import { ProtectedLayout } from "../components/layout/ProtectedLayout";
import { AuthProvider } from "../store/auth-context";
import { LoginPage } from "./auth/LoginPage";
import { SignupPage } from "./auth/SignupPage";
import { DashboardPage } from "./dashboard/DashboardPage";
import { NotesPage } from "./notes/NotesPage";
import { PomodoroPage } from "./pomodoro/PomodoroPage";
import { StudySessionsPage } from "./sessions/StudySessionsPage";
import { SubjectsPage } from "./subjects/SubjectsPage";
import { TasksPage } from "./tasks/TasksPage";

export function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/signup" element={<SignupPage />} />

          <Route element={<ProtectedLayout />}>
            <Route path="/" element={<DashboardPage />} />
            <Route path="/subjects" element={<SubjectsPage />} />
            <Route path="/tasks" element={<TasksPage />} />
            <Route path="/study-sessions" element={<StudySessionsPage />} />
            <Route path="/pomodoro" element={<PomodoroPage />} />
            <Route path="/notes" element={<NotesPage />} />
          </Route>

          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
