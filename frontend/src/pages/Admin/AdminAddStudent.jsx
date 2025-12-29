// src/pages/Admin/AdminAddStudent.jsx
import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../../services/api";

export default function AdminAddStudent() {
  const navigate = useNavigate();

  const [form, setForm] = useState({
    roll_no: "",
    name: "",
    division: "",
    optional_subject: "None",
    optional_subject_2: "None",
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await api.post("/admin/students", {
        roll_no: form.roll_no,
        name: form.name,
        division: form.division.toUpperCase(),
        optional_subject: form.optional_subject,
        optional_subject_2: form.optional_subject_2,
      });

      alert("Student added successfully");
      navigate("/admin/students");
    } catch (err) {
      alert("Failed to add student (maybe duplicate roll/division)");
    }
  };

  return (
    <div style={{ padding: "20px" }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
        <button onClick={() => navigate('/admin')} style={{ padding: '6px 10px' }}>Go Back</button>
        <h2 style={{ margin: 0 }}>Add Student</h2>
        <div style={{ width: 80 }} />
      </div>

      <form onSubmit={handleSubmit} style={{ maxWidth: "400px" }}>
        <div>
          <label>Roll No</label><br />
          <input
            name="roll_no"
            value={form.roll_no}
            onChange={handleChange}
            required
          />
        </div>

        <div>
          <label>Name</label><br />
          <input
            name="name"
            value={form.name}
            onChange={handleChange}
            required
          />
        </div>

        <div>
          <label>Division</label><br />
          <input
            name="division"
            value={form.division}
            onChange={handleChange}
            required
            placeholder="A / B / C"
          />
        </div>

        <div>
          <label>Optional Subject (Hindi / IT)</label><br />
          <select
            name="optional_subject"
            value={form.optional_subject}
            onChange={handleChange}
          >
            <option value="None">None</option>
            <option value="HINDI">Hindi</option>
            <option value="IT">IT</option>
          </select>
        </div>

        <div>
          <label>Optional Subject 2 (Maths / SP)</label><br />
          <select
            name="optional_subject_2"
            value={form.optional_subject_2}
            onChange={handleChange}
          >
            <option value="None">None</option>
            <option value="MATHS">Mathematics</option>
            <option value="SP">SP</option>
          </select>
        </div>

        <div style={{ marginTop: "15px" }}>
          <button type="submit">Save</button>{" "}
          <button type="button" onClick={() => navigate("/admin")}>
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
}
