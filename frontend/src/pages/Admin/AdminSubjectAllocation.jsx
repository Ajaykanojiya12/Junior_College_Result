// src/pages/Admin/AdminSubjectAllocation.jsx
import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../../services/api";

export default function AdminSubjectAllocation() {
  const navigate = useNavigate();
  const [teachers, setTeachers] = useState([]);
  const [subjects, setSubjects] = useState([]);
  const [allocations, setAllocations] = useState([]);

  const [form, setForm] = useState({
    teacher_id: "",
    subject_id: "",
    division: "",
  });

  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    try {
      const [tRes, sRes, aRes] = await Promise.all([
        api.get("/admin/teachers"),
        api.get("/subjects"),
        api.get("/admin/allocations"),
      ]);

      setTeachers(tRes.data);
      setSubjects(sRes.data);
      setAllocations(aRes.data);
    } catch (err) {
      alert("Failed to load data");
    }
  };

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await api.post("/admin/allocations", {
        teacher_id: parseInt(form.teacher_id),
        subject_id: parseInt(form.subject_id),
        division: form.division.toUpperCase(),
      });

      setForm({ teacher_id: "", subject_id: "", division: "" });
      loadInitialData();
    } catch (err) {
      alert("Allocation failed (maybe duplicate)");
    }
  };

  return (
    <div style={{ padding: "20px" }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
        <button onClick={() => navigate('/admin')} style={{ padding: '6px 10px' }}>Go Back</button>
        <h2 style={{ margin: 0 }}>Allocate Teacher to Subject & Division</h2>
        <div style={{ width: 80 }} />
      </div>

      <form onSubmit={handleSubmit} style={{ marginBottom: "20px" }}>
        <select
          name="teacher_id"
          value={form.teacher_id}
          onChange={handleChange}
          required
        >
          <option value="">Select Teacher</option>
          {teachers.map((t) => (
            <option key={t.teacher_id} value={t.teacher_id}>
              {t.name} ({t.userid})
            </option>
          ))}
        </select>{" "}

        <select
          name="subject_id"
          value={form.subject_id}
          onChange={handleChange}
          required
        >
          <option value="">Select Subject</option>
          {subjects.map((s) => (
            <option key={s.subject_id} value={s.subject_id}>
              {s.subject_code} - {s.subject_name}
            </option>
          ))}
        </select>{" "}

        <input
          name="division"
          placeholder="Division (A/B/...)"
          value={form.division}
          onChange={handleChange}
          required
        />{" "}

        <button type="submit">Allocate</button>
      </form>

      <h3>Current Allocations</h3>

      <table border="1" cellPadding="6">
        <thead>
          <tr>
            <th>Teacher</th>
            <th>Subject</th>
            <th>Division</th>
          </tr>
        </thead>
        <tbody>
          {allocations.map((a, idx) => (
            <tr key={idx}>
              <td>{a.teacher_id}</td>
              <td>{a.subject_id}</td>
              <td>{a.division}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
