// src/routes.jsx
import React from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { useAuth } from "./context/AuthContext";

import LoginPage from "./pages/LoginPage";

// Admin pages
import AdminDashboard from "./pages/Admin/AdminDashboard";
import AdminTeacherList from "./pages/Admin/AdminTeacherList";
import AdminAddTeacher from "./pages/Admin/AdminAddTeacher";
import AdminEditTeacher from "./pages/Admin/AdminEditTeacher";
import AdminSubjectAllocation from "./pages/Admin/AdminSubjectAllocation";
import AdminAddStudent from "./pages/Admin/AdminAddStudent";
import AdminViewStudents from "./pages/Admin/AdminViewStudents";
import AdminViewCompleteResult from "./pages/Admin/ViewCompleteResult";

// Teacher pages
import TeacherDashboard from "./pages/Teacher/TeacherDashboard";
import UpdateMarks from "./pages/Teacher/UpdateMarks";
import ViewCompleteResult from "./pages/Teacher/ViewCompleteResult";
import SubjectResult from "./pages/Teacher/SubjectResult";

function ProtectedRoute({ children, requiredRole }) {
  const { user } = useAuth();

  if (!user) {
    return <Navigate to="/" replace />;
  }

  // Allow ADMIN to access any route; otherwise require exact role match when provided
  if (requiredRole && user.role !== requiredRole && user.role !== "ADMIN") {
    return <Navigate to="/" replace />;
  }

  return children;
}

export default function AppRoutes() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LoginPage />} />

        {/* ---------------- ADMIN ---------------- */}
        <Route
          path="/admin"
          element={
            <ProtectedRoute requiredRole="ADMIN">
              <AdminDashboard />
            </ProtectedRoute>
          }
        />

        <Route
          path="/admin/teachers"
          element={
            <ProtectedRoute requiredRole="ADMIN">
              <AdminTeacherList />
            </ProtectedRoute>
          }
        />

        <Route
          path="/admin/teachers/add"
          element={
            <ProtectedRoute requiredRole="ADMIN">
              <AdminAddTeacher />
            </ProtectedRoute>
          }
        />

        <Route
          path="/admin/teachers/edit/:id"
          element={
            <ProtectedRoute requiredRole="ADMIN">
              <AdminEditTeacher />
            </ProtectedRoute>
          }
        />

        <Route
          path="/admin/allocations"
          element={
            <ProtectedRoute requiredRole="ADMIN">
              <AdminSubjectAllocation />
            </ProtectedRoute>
          }
        />

        <Route
          path="/admin/students/add"
          element={
            <ProtectedRoute requiredRole="ADMIN">
              <AdminAddStudent />
            </ProtectedRoute>
          }
        />

        <Route
          path="/admin/students"
          element={
            <ProtectedRoute requiredRole="ADMIN">
              <AdminViewStudents />
            </ProtectedRoute>
          }
        />

        <Route
          path="/admin/results"
          element={
            <ProtectedRoute requiredRole="ADMIN">
              <AdminViewCompleteResult />
            </ProtectedRoute>
          }
        />

        {/* ---------------- TEACHER ---------------- */}
        <Route
          path="/teacher"
          element={
            <ProtectedRoute requiredRole="TEACHER">
              <TeacherDashboard />
            </ProtectedRoute>
          }
        />

        <Route
          path="/teacher/add-marks"
          element={
            <ProtectedRoute requiredRole="TEACHER">
              <UpdateMarks />
            </ProtectedRoute>
          }
        />
        <Route
          path="/teacher/subject-result"
          element={
            <ProtectedRoute requiredRole="TEACHER">
              <SubjectResult />
            </ProtectedRoute>
          }
        />

        <Route
          path="/teacher/view-complete-result"
          element={
            <ProtectedRoute requiredRole="ADMIN">
              <ViewCompleteResult />
            </ProtectedRoute>
          }
        />
      </Routes>
    </BrowserRouter>
  );
}
