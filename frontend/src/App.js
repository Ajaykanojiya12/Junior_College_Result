// src/App.js
import React from "react";
import { AuthProvider } from "./context/AuthContext";
import { NotificationProvider } from "./context/NotificationContext";
import AppRoutes from "./routes";
import Toast from "./components/ui/Toast";

function App() {
  return (
    <AuthProvider>
      <NotificationProvider>
        <Toast />
        <AppRoutes />
      </NotificationProvider>
    </AuthProvider>
  );
}

export default App;
