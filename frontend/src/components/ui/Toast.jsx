// src/components/ui/Toast.jsx
import React from "react";
import { useNotification } from "../../context/NotificationContext";
import styles from "./Toast.module.css";

export default function Toast() {
  const { notifications, removeNotification } = useNotification();

  return (
    <div className={styles.toastContainer}>
      {notifications.map((notification) => (
        <div
          key={notification.id}
          className={`${styles.toast} ${styles[notification.type]}`}
        >
          <div className={styles.content}>{notification.message}</div>
          <button
            className={styles.close}
            onClick={() => removeNotification(notification.id)}
            aria-label="Close notification"
          >
            ×
          </button>
        </div>
      ))}
    </div>
  );
}
