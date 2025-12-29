// src/context/NotificationContext.jsx
import React, { createContext, useState, useContext, useCallback } from "react";

const NotificationContext = createContext(null);

export function NotificationProvider({ children }) {
  const [notifications, setNotifications] = useState([]);

  const addNotification = useCallback((message, type = "info", duration = 3000) => {
    const id = Date.now();
    const notification = { id, message, type };

    setNotifications((prev) => [...prev, notification]);

    if (duration > 0) {
      setTimeout(() => {
        // avoid depending on removeNotification reference; update state directly
        setNotifications((prev) => prev.filter((n) => n.id !== id));
      }, duration);
    }

    return id;
  }, []);

  const removeNotification = useCallback((id) => {
    setNotifications((prev) => prev.filter((n) => n.id !== id));
  }, []);

  const success = useCallback((message, duration) => {
    return addNotification(message, "success", duration);
  }, [addNotification]);

  const error = useCallback((message, duration) => {
    return addNotification(message, "error", duration);
  }, [addNotification]);

  const warning = useCallback((message, duration) => {
    return addNotification(message, "warning", duration);
  }, [addNotification]);

  const info = useCallback((message, duration) => {
    return addNotification(message, "info", duration);
  }, [addNotification]);

  const value = {
    notifications,
    addNotification,
    removeNotification,
    success,
    error,
    warning,
    info,
  };

  return (
    <NotificationContext.Provider value={value}>
      {children}
    </NotificationContext.Provider>
  );
}

export function useNotification() {
  const ctx = useContext(NotificationContext);
  if (ctx === undefined) {
    throw new Error("useNotification must be used within NotificationProvider");
  }
  return ctx;
}
