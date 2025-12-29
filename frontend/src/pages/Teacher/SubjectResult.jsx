import React, { useEffect, useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import api from '../../services/api';
import { useAuth } from '../../context/AuthContext';

export default function SubjectResult() {
  useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [allocations, setAllocations] = useState([]);
  const [subjectId, setSubjectId] = useState('');
  const [division, setDivision] = useState('A');
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(false);
  const [search, setSearch] = useState('');

  useEffect(() => {
    async function load() {
      try {
        const res = await api.get('/auth/me');
        const alloc = res.data.allocations || [];
        setAllocations(alloc);
        const qp = new URLSearchParams(location.search);
        const sid = qp.get('subject_id');
        const divq = qp.get('division');
        if (sid) setSubjectId(sid);
        if (divq) setDivision(divq);
        if (!sid && alloc.length>0) setSubjectId(alloc[0].subject_id);
      } catch (err) {
        setAllocations([]);
      }
    }
    load();
  }, [location.search]);

  useEffect(() => {
    async function loadMarks() {
      if (!subjectId || !division) return;
      setLoading(true);
      try {
        const res = await api.get('/teacher/marks', { params: { subject_id: subjectId, division } });
        setRows(res.data || []);
      } catch (err) {
        setRows([]);
      } finally {
        setLoading(false);
      }
    }
    loadMarks();
  }, [subjectId, division]);

  return (
    <div style={{ padding: 20 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
        <button onClick={() => navigate('/teacher')} style={{ padding: '6px 10px' }}>Go Back</button>
        <h2 style={{ margin: 0 }}>Subject Results</h2>
        <div style={{ width: 80 }} />
      </div>

      <div style={{ display: 'flex', gap: 12, marginBottom: 12, alignItems: 'center' }}>
        <div>
          <label style={{ fontWeight: 600 }}>Subject</label><br />
          <select value={subjectId} onChange={e => setSubjectId(e.target.value)}>
            <option value="">-- select --</option>
            {allocations.map(a => (
              <option key={a.subject_id} value={a.subject_id}>{a.subject_code} — {a.subject_name}</option>
            ))}
          </select>
        </div>

        <div>
          <label style={{ fontWeight: 600 }}>Division</label><br />
          <select value={division} onChange={e => setDivision(e.target.value)}>
            {Array.from(new Set(allocations.map(a => a.division))).map(d => (
              <option key={d} value={d}>{d}</option>
            ))}
          </select>
        </div>

        <div style={{ marginLeft: 'auto' }}>
          <label style={{ fontWeight: 600 }}>Search Roll</label><br />
          <input value={search} onChange={e => setSearch(e.target.value)} placeholder="Roll no" />
        </div>
      </div>

      {loading && <div>Loading...</div>}

      {!loading && rows.length === 0 && <div style={{ color: '#666' }}>No marks found for the selected subject/division.</div>}

      {!loading && rows.length > 0 && (
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ background: '#f7f9fb' }}>
              <th style={{ padding: 8, textAlign: 'left' }}>Roll</th>
              <th style={{ padding: 8, textAlign: 'left' }}>Name</th>
              <th style={{ padding: 8, textAlign: 'center' }}>Unit1</th>
              <th style={{ padding: 8, textAlign: 'center' }}>Unit2</th>
              <th style={{ padding: 8, textAlign: 'center' }}>Terminal</th>
              <th style={{ padding: 8, textAlign: 'center' }}>Annual</th>
              <th style={{ padding: 8, textAlign: 'center' }}>Grace</th>
            </tr>
          </thead>
          <tbody>
            {rows.filter(r => !search || String(r.roll_no).includes(search)).map(r => (
              <tr key={r.roll_no} style={{ borderBottom: '1px solid #eee' }}>
                <td style={{ padding: 8 }}>{r.roll_no}</td>
                <td style={{ padding: 8 }}>{r.name}</td>
                <td style={{ padding: 6, textAlign: 'center' }}>{r.mark.unit1 ?? '-'}</td>
                <td style={{ padding: 6, textAlign: 'center' }}>{r.mark.unit2 ?? '-'}</td>
                <td style={{ padding: 6, textAlign: 'center' }}>{r.mark.term ?? '-'}</td>
                <td style={{ padding: 6, textAlign: 'center' }}>{r.mark.annual ?? '-'}</td>
                <td style={{ padding: 6, textAlign: 'center', color: r.mark.grace ? '#c0392b' : '#666' }}>{r.mark.grace ?? 0}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
