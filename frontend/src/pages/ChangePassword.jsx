// frontend/src/pages/ChangePassword.jsx
import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useNotification } from "../context/NotificationContext";
import { validateForm, validators } from "../utils/validators";
import Spinner from "../components/ui/Spinner";
import api from "../services/api";

export default function ChangePassword() {
  const navigate = useNavigate();
  const { logout } = useAuth();
  const { success, error } = useNotification();
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});
  const [formData, setFormData] = useState({
    old_password: "",
    new_password: "",
    confirm_password: "",
  });

  const validationRules = {
    old_password: [validators.required],
    new_password: [
      validators.required,
      validators.minLength(6),
      validators.password,
    ],
    confirm_password: [validators.required],
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    // Clear error for this field when user starts typing
    if (errors[name]) {
      setErrors((prev) => ({ ...prev, [name]: null }));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Validate form
    const validationErrors = validateForm(formData, validationRules);
    if (Object.keys(validationErrors).length > 0) {
      setErrors(validationErrors);
      return;
    }

    // Check if passwords match
    if (formData.new_password !== formData.confirm_password) {
      setErrors({
        confirm_password: "Passwords do not match",
      });
      error("Passwords do not match");
      return;
    }

    setLoading(true);
    try {
      const response = await api.post("/admin/change-password", formData);

      if (response.status === 200) {
        success("Password changed successfully!");
        setFormData({
          old_password: "",
          new_password: "",
          confirm_password: "",
        });
        setErrors({});

        // Optionally redirect or logout
        setTimeout(() => {
          window.location.href = "/admin/dashboard";
        }, 1500);
      }
    } catch (err) {
      const errorMsg =
        err.response?.data?.error || "Failed to change password";
      error(errorMsg);
      setErrors({ submit: errorMsg });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: "500px", margin: "0 auto", padding: "40px 20px" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "30px" }}>
        <h1 style={{ margin: 0 }}>Change Password</h1>
        <button
          onClick={() => navigate("/admin")}
          style={{
            padding: "8px 16px",
            background: "#6c757d",
            color: "white",
            border: "none",
            borderRadius: "4px",
            cursor: "pointer"
          }}
        >
          Back
        </button>
      </div>
      <p style={{ color: "#666", marginBottom: "30px" }}>
        Update your password to secure your account
      </p>

      <form onSubmit={handleSubmit}>
        {/* Old Password */}
        <div style={{ marginBottom: "20px" }}>
          <label style={{ display: "block", marginBottom: "8px", fontWeight: "500" }}>
            Current Password
          </label>
          <input
            type="password"
            name="old_password"
            value={formData.old_password}
            onChange={handleChange}
            placeholder="Enter your current password"
            style={{
              width: "100%",
              padding: "10px",
              border: errors.old_password ? "2px solid #e74c3c" : "1px solid #ccc",
              borderRadius: "4px",
              fontSize: "14px",
              boxSizing: "border-box",
            }}
          />
          {errors.old_password && (
            <span style={{ color: "#e74c3c", fontSize: "12px" }}>
              {errors.old_password}
            </span>
          )}
        </div>

        {/* New Password */}
        <div style={{ marginBottom: "20px" }}>
          <label style={{ display: "block", marginBottom: "8px", fontWeight: "500" }}>
            New Password
          </label>
          <input
            type="password"
            name="new_password"
            value={formData.new_password}
            onChange={handleChange}
            placeholder="Enter new password (min 6 characters)"
            style={{
              width: "100%",
              padding: "10px",
              border: errors.new_password ? "2px solid #e74c3c" : "1px solid #ccc",
              borderRadius: "4px",
              fontSize: "14px",
              boxSizing: "border-box",
            }}
          />
          {errors.new_password && (
            <span style={{ color: "#e74c3c", fontSize: "12px" }}>
              {errors.new_password}
            </span>
          )}
          <p style={{ fontSize: "12px", color: "#666", marginTop: "5px" }}>
            Password must contain: uppercase, lowercase, number, and be at least 6 characters
          </p>
        </div>

        {/* Confirm Password */}
        <div style={{ marginBottom: "30px" }}>
          <label style={{ display: "block", marginBottom: "8px", fontWeight: "500" }}>
            Confirm Password
          </label>
          <input
            type="password"
            name="confirm_password"
            value={formData.confirm_password}
            onChange={handleChange}
            placeholder="Confirm your new password"
            style={{
              width: "100%",
              padding: "10px",
              border: errors.confirm_password ? "2px solid #e74c3c" : "1px solid #ccc",
              borderRadius: "4px",
              fontSize: "14px",
              boxSizing: "border-box",
            }}
          />
          {errors.confirm_password && (
            <span style={{ color: "#e74c3c", fontSize: "12px" }}>
              {errors.confirm_password}
            </span>
          )}
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={loading}
          style={{
            width: "100%",
            padding: "12px",
            background: loading ? "#95a5a6" : "#3498db",
            color: "white",
            border: "none",
            borderRadius: "4px",
            fontSize: "16px",
            fontWeight: "500",
            cursor: loading ? "not-allowed" : "pointer",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            gap: "10px",
          }}
        >
          {loading && <Spinner size="small" text="" />}
          {loading ? "Changing..." : "Change Password"}
        </button>
      </form>

      <div style={{ marginTop: "30px", padding: "20px", background: "#ecf0f1", borderRadius: "4px" }}>
        <h4 style={{ margin: "0 0 10px 0" }}>Password Requirements:</h4>
        <ul style={{ margin: "0", paddingLeft: "20px", fontSize: "14px" }}>
          <li>At least 6 characters</li>
          <li>Contains uppercase letter (A-Z)</li>
          <li>Contains lowercase letter (a-z)</li>
          <li>Contains number (0-9)</li>
        </ul>
      </div>
    </div>
  );
}
