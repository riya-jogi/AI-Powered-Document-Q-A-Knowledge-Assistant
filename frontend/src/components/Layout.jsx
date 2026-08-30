import { NavLink, Outlet, useNavigate } from 'react-router-dom';
import { api } from '../api';

export default function Layout() {
  const navigate = useNavigate();

  const handleLogout = () => {
    api.logout();
    navigate('/login');
  };

  return (
    <div className="layout">
      <aside className="sidebar">
        <h1>DocuMind</h1>
        <nav>
          <NavLink to="/" end>Dashboard</NavLink>
          <NavLink to="/documents">Documents</NavLink>
          <NavLink to="/chat">Chat</NavLink>
        </nav>
        <div style={{ marginTop: 'auto' }}>
          <button className="btn-secondary" onClick={handleLogout} style={{ width: '100%' }}>
            Logout
          </button>
        </div>
      </aside>
      <main className="main">
        <Outlet />
      </main>
    </div>
  );
}
