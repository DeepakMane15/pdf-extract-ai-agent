import { NavLink, Outlet, useNavigate } from 'react-router-dom';

import { useAuth } from '../context/AuthContext';
import type { UserRole } from '../api/types';

function roleLabel(role: UserRole): string {
  return role;
}

export function Layout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const canPdf = user?.role === 'admin' || user?.role === 'auditor';
  const canUsers = user?.role === 'admin' || user?.role === 'auditor';

  const handleLogout = () => {
    logout();
    navigate('/login', { replace: true });
  };

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="sidebar-brand">
          <h1>RAG Console</h1>
          <p>Documents · Search · Chat</p>
        </div>
        <nav className="sidebar-nav">
          <NavLink to="/" end className={({ isActive }) => (isActive ? 'active' : undefined)}>
            Overview
          </NavLink>
          <NavLink to="/search" className={({ isActive }) => (isActive ? 'active' : undefined)}>
            Search
          </NavLink>
          <NavLink to="/chat" className={({ isActive }) => (isActive ? 'active' : undefined)}>
            Chat
          </NavLink>
          <NavLink to="/pdf/list" className={({ isActive }) => (isActive ? 'active' : undefined)}>
            PDF listing
          </NavLink>
          {canPdf ? (
            <NavLink to="/pdf" className={({ isActive }) => (isActive ? 'active' : undefined)}>
              PDF ingest
            </NavLink>
          ) : null}
          {canUsers ? (
            <NavLink to="/users" className={({ isActive }) => (isActive ? 'active' : undefined)}>
              Users
            </NavLink>
          ) : null}
          <NavLink to="/tools" className={({ isActive }) => (isActive ? 'active' : undefined)}>
            Tools
          </NavLink>
        </nav>
      </aside>
      <div className="main-area">
        <header className="top-bar">
          {user ? (
            <>
              <span className="top-bar-user">
                {user.email}
                <span className="badge badge-accent" style={{ marginLeft: 8 }}>
                  {roleLabel(user.role)}
                </span>
              </span>
              <button type="button" className="btn btn-ghost btn-danger" onClick={handleLogout}>
                Sign out
              </button>
            </>
          ) : null}
        </header>
        <main>
          <Outlet />
        </main>
      </div>
    </div>
  );
}
