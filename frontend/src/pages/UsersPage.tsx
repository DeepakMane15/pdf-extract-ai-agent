import { useCallback, useEffect, useState, type FormEvent } from 'react';
import { Navigate } from 'react-router-dom';

import { apiFetch, ApiError } from '../api/client';
import type { UserRead, UserRole } from '../api/types';
import { useAuth } from '../context/AuthContext';

export function UsersPage() {
  const { user } = useAuth();
  const canList = user?.role === 'admin' || user?.role === 'auditor';
  const canCreate = user?.role === 'admin';

  const [users, setUsers] = useState<UserRead[]>([]);
  const [loadErr, setLoadErr] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [role, setRole] = useState<UserRole>('user');
  const [createErr, setCreateErr] = useState<string | null>(null);
  const [createOk, setCreateOk] = useState<string | null>(null);
  const [creating, setCreating] = useState(false);

  const load = useCallback(async () => {
    setLoadErr(null);
    setLoading(true);
    try {
      const list = await apiFetch<UserRead[]>('/users');
      setUsers(list);
    } catch (e) {
      setLoadErr(e instanceof ApiError ? e.message : 'Failed to load users');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (canList) void load();
  }, [canList, load]);

  if (!canList) {
    return <Navigate to="/" replace />;
  }

  async function onCreate(e: FormEvent) {
    e.preventDefault();
    setCreateErr(null);
    setCreateOk(null);
    setCreating(true);
    try {
      await apiFetch<UserRead>('/users', {
        method: 'POST',
        json: {
          email: email.trim(),
          password,
          full_name: fullName.trim() || null,
          role,
        },
      });
      setCreateOk(`Created ${email.trim()}`);
      setEmail('');
      setPassword('');
      setFullName('');
      setRole('user');
      await load();
    } catch (err) {
      setCreateErr(err instanceof ApiError ? err.message : 'Create failed');
    } finally {
      setCreating(false);
    }
  }

  return (
    <div className="page">
      <h1 className="page-title">Users</h1>
      <p className="page-desc">Directory accounts (admin/auditor can view; only admin can create).</p>

      {loadErr ? <div className="alert alert-error">{loadErr}</div> : null}

      <div className="card">
        <h3>All users</h3>
        {loading ? (
          <p className="page-desc" style={{ margin: 0 }}>
            Loading…
          </p>
        ) : (
          <div className="table-wrap">
            <table className="data">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Email</th>
                  <th>Name</th>
                  <th>Role</th>
                  <th>Active</th>
                </tr>
              </thead>
              <tbody>
                {users.map((u) => (
                  <tr key={u.id}>
                    <td>{u.id}</td>
                    <td>{u.email}</td>
                    <td>{u.full_name ?? '—'}</td>
                    <td>
                      <span className="badge badge-accent">{u.role}</span>
                    </td>
                    <td>{u.is_active ? 'Yes' : 'No'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {canCreate ? (
        <div className="card">
          <h3>Create user</h3>
          {createErr ? <div className="alert alert-error">{createErr}</div> : null}
          {createOk ? <div className="alert alert-success">{createOk}</div> : null}
          <form onSubmit={onCreate}>
            <div className="field">
              <label htmlFor="cemail">Email</label>
              <input
                id="cemail"
                className="input"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>
            <div className="field">
              <label htmlFor="cpass">Password</label>
              <input
                id="cpass"
                className="input"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                minLength={6}
              />
            </div>
            <div className="field">
              <label htmlFor="cname">Full name (optional)</label>
              <input
                id="cname"
                className="input"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
              />
            </div>
            <div className="field">
              <label htmlFor="crole">Role</label>
              <select id="crole" className="select" value={role} onChange={(e) => setRole(e.target.value as UserRole)}>
                <option value="user">user</option>
                <option value="auditor">auditor</option>
                <option value="admin">admin</option>
              </select>
            </div>
            <button type="submit" className="btn btn-primary" disabled={creating}>
              {creating ? 'Creating…' : 'Create user'}
            </button>
          </form>
        </div>
      ) : null}
    </div>
  );
}
