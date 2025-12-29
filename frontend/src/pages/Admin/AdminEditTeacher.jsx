// src/pages/Admin/AdminEditTeacher.jsx
import React, { useEffect, useState, useCallback } from "react";
import { useNavigate, useParams } from "react-router-dom";
import api from "../../services/api";

export default function AdminEditTeacher() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [form, setForm] = useState({
    name: "",
    userid: "",
    email: "",
    password: "",
    active: true,
  });
  const [showPassword, setShowPassword] = useState(false);

  const loadTeacher = useCallback(async () => {
    try {
      const res = await api.get("/admin/teachers");
      const teacher = res.data.find((t) => t.teacher_id === parseInt(id));
      if (!teacher) {
        alert("Teacher not found");
        navigate("/admin/teachers");
        return;
      }
      setForm({
        name: teacher.name,
        userid: teacher.userid,
        email: teacher.email || "",
        password: "",
        active: teacher.active,
      });
    } catch (err) {
      alert("Failed to load teacher");
    }
  }, [id, navigate]);

  useEffect(() => {
    loadTeacher();
  }, [loadTeacher]);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setForm((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const payload = { ...form };
      if (!payload.password) delete payload.password;

      await api.put(`/admin/teachers/${id}`, payload);
      navigate("/admin/teachers");
    } catch (err) {
      alert("Failed to update teacher");
    }
  };

  return (
    <div style={{ padding: "20px" }}>
      <h2>Edit Teacher</h2>

      <form onSubmit={handleSubmit}>
        <div>
          <label>Name</label><br />
          <input name="name" value={form.name} onChange={handleChange} required />
        </div>

        <div>
          <label>User ID</label><br />
          <input name="userid" value={form.userid} onChange={handleChange} required />
        </div>

        <div>
          <label>Email</label><br />
          <input name="email" value={form.email} onChange={handleChange} />
        </div>

        <div style={{ position: 'relative' }}>
          <label>New Password</label><br />
          <input
            type={showPassword ? 'text' : 'password'}
            name="password"
            value={form.password}
            onChange={handleChange}
            placeholder="password"
            style={{ paddingRight: 44 }}
            autoComplete="new-password"
          />
          <button
            type="button"
            onClick={() => setShowPassword((s) => !s)}
            style={{
              position: "absolute",
              right: 8,
              top: "50%",
              transform: "translateY(-50%)",
              background: "none",
              border: "none",
              cursor: "pointer",
              padding: 4,
              lineHeight: 1,
            }}
            aria-pressed={showPassword}
            aria-label={showPassword ? "Hide password" : "Show password"}
            title={showPassword ? "Hide password" : "Show password"}
          >
            {showPassword ? "Hide" : "Show"}
          </button>
        </div>

        <div>
          <label>
            <input
              type="checkbox"
              name="active"
              checked={form.active}
              onChange={handleChange}
            />
            Active
          </label>
        </div>

        <button type="submit">Save</button>{" "}
        <button type="button" onClick={() => navigate("/admin/teachers")}>
          Cancel
        </button>
      </form>
    </div>
  );
}