// src/components/auth/LoginSelector.jsx
import React from "react";

function LoginSelector({ role, setRole }) {
  return (
    <div style={{ display: "flex", gap: "10px", marginBottom: "20px" }}>
      <button
        type="button"
        onClick={() => setRole("teacher")}
        style={{
          padding: "8px 16px",
          background: role === "teacher" ? "#007bff" : "#e0e0e0",
          color: role === "teacher" ? "white" : "black",
          border: "none",
          borderRadius: "4px",
          cursor: "pointer",
        }}
      >
        Teacher Login
      </button>

      <button
        type="button"
        onClick={() => setRole("admin")}
        style={{
          padding: "8px 16px",
          background: role === "admin" ? "#007bff" : "#e0e0e0",
          color: role === "admin" ? "white" : "black",
          border: "none",
          borderRadius: "4px",
          cursor: "pointer",
        }}
      >
        Admin Login
      </button>
    </div>
  );
}

export default LoginSelector;
