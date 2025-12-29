// src/pages/Admin/AdminAddTeacher.jsx
import React, { useState } from "react";
import api from "../../services/api";
import { useAuth } from "../../context/AuthContext";
import { useNavigate } from "react-router-dom";

const logoUrl = "/mnt/data/5da5c281-cfb7-4452-b683-07f8b06b2d05.png";

export default function AdminAddTeacher() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [name, setName] = useState("");
  const [userid, setUserid] = useState("");
  const [password, setPassword] = useState("");
  const [email, setEmail] = useState("");
  const [msg, setMsg] = useState("");
  const [loading, setLoading] = useState(false);
  const [createAnother, setCreateAnother] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setMsg("");

    if (!name || !userid || !password) {
      setMsg("Please fill all required fields.");
      return;
    }

    setLoading(true);
    try {
      await api.post("/admin/teachers", {
        name,
        userid,
        password,
        email: email || null,
      });

      setMsg("Teacher added successfully!");
      if (createAnother) {
        // clear form for next entry
        setName("");
        setUserid("");
        setPassword("");
        setEmail("");
        // keep focus for next add
      } else {
        // Redirect to teacher list after a short delay
        setTimeout(() => {
          window.location.href = "/admin/teachers";
        }, 1000);
      }
    } catch (err) {
      console.error(err);
      setMsg(err.response?.data?.error || "Failed to add teacher.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ padding: 20 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
        <button onClick={() => navigate('/admin')} style={{ padding: '6px 10px' }}>Go Back</button>
        <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
          <img src={logoUrl} alt="logo" style={{ width: 64, height: 'auto' }} />
          <h3 style={{ margin: 0 }}>Add Teacher</h3>
        </div>
        <div style={{ width: 80 }} />
      </div>

      <p style={{ color: "#555" }}>Logged in as: {user?.userid}</p>

      <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: 10, maxWidth: 420 }}>
        <div>
          <label style={{ display: "block", marginBottom: 4, fontWeight: "bold" }}>
            Full Name *
          </label>
          <input
            type="text"
            placeholder="e.g. John Doe"
            value={name}
            onChange={(e) => setName(e.target.value)}
            style={{ padding: 8, width: "100%", boxSizing: "border-box" }}
          />
        </div>

        <div>
          <label style={{ display: "block", marginBottom: 4, fontWeight: "bold" }}>
            User ID *
          </label>
          <input
            type="text"
            placeholder="e.g. john_doe or teacher01"
            value={userid}
            onChange={(e) => setUserid(e.target.value)}
            style={{ padding: 8, width: "100%", boxSizing: "border-box" }}
          />
        </div>

        <div>
          <label style={{ display: "block", marginBottom: 4, fontWeight: "bold" }}>
            Password *
          </label>
          <input
            type="password"
            placeholder="Minimum 6 characters"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            style={{ padding: 8, width: "100%", boxSizing: "border-box" }}
          />
        </div>

        <div>
          <label style={{ display: "block", marginBottom: 4, fontWeight: "bold" }}>
            Email (Optional)
          </label>
          <input
            type="email"
            placeholder="e.g. john@example.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            style={{ padding: 8, width: "100%", boxSizing: "border-box" }}
          />
        </div>

        <p style={{ fontSize: 12, color: "#666", fontStyle: "italic", marginTop: 10 }}>
          📝 Note: Subjects will be allocated to this teacher from the Subject Allocation page.
        </p>

        <button
          type="submit"
          disabled={loading}
          style={{
            padding: "10px",
            background: "#007bff",
            color: "white",
            border: "none",
            borderRadius: 4,
            cursor: "pointer"
          }}
        >
          {loading ? "Adding..." : "Add Teacher"}
        </button>
      </form>

      <div style={{ marginTop: 8 }}>
        <label style={{ fontSize: 13 }}>
          <input type="checkbox" checked={createAnother} onChange={e => setCreateAnother(e.target.checked)} />{' '}
          Create another after saving
        </label>
      </div>

      {msg && <div style={{ marginTop: 12, color: msg.includes("successfully") ? "green" : "red" }}>{msg}</div>}
    </div>
  );
}
