// src/pages/Admin/AdminViewStudents.jsx
import React, { useState } from "react";
import api from "../../services/api";
import { useNavigate } from "react-router-dom";

export default function AdminViewStudents() {
  const navigate = useNavigate();
  const [division, setDivision] = useState("");
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(false);

  const loadStudents = async () => {
    if (!division) {
      alert("Please enter a division");
      return;
    }

    try {
      setLoading(true);
      const res = await api.get(`/admin/students?division=${division.toUpperCase()}`);
      setStudents(res.data);
    } catch (err) {
      alert("Failed to load students");
      setStudents([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: "20px" }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
        <button onClick={() => navigate('/admin')} style={{ padding: '6px 10px' }}>Go Back</button>
        <h2 style={{ margin: 0 }}>View Students</h2>
        <div style={{ width: 80 }} />
      </div>

      <div style={{ marginBottom: "15px" }}>
        <input
          placeholder="Division (A / B / C)"
          value={division}
          onChange={(e) => setDivision(e.target.value)}
        />{" "}
        <button onClick={loadStudents}>Load</button>
      </div>

      {loading && <p>Loading...</p>}

      {!loading && students.length === 0 && (
        <p>No students found.</p>
      )}

      {students.length > 0 && (
        <table border="1" cellPadding="8">
          <thead>
            <tr>
              <th>Roll No</th>
              <th>Name</th>
              <th>Division</th>
              <th>Optional Subject</th>
              <th>Optional Subject 2</th>
            </tr>
          </thead>
          <tbody>
            {students.map((s, idx) => (
              <tr key={idx}>
                <td>{s.roll_no}</td>
                <td>{s.name}</td>
                <td>{s.division}</td>
                <td>{s.optional_subject || "-"}</td>
                <td>{s.optional_subject_2 || "-"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
