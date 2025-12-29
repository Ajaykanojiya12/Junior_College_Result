// src/components/ui/Spinner.jsx
import React from "react";
import styles from "./Spinner.module.css";

/**
 * Loading spinner component
 */
export default function Spinner({ size = "medium", text = "Loading..." }) {
  return (
    <div className={`${styles.spinner} ${styles[size]}`}>
      <div className={styles.spinnerInner}></div>
      {text && <p className={styles.text}>{text}</p>}
    </div>
  );
}
