// src/components/Navbar.js
import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from './AuthProvider';
import './Navbar.css';
import { FaUserCircle } from 'react-icons/fa';

function Navbar() {
  const { currentUser, logout } = useAuth();
  const navigate = useNavigate();

  async function handleLogout() {
    try {
      await logout();
      navigate('/login');
    } catch {
      alert('Failed to log out');
    }
  }

  return (
    <div className="navbar">
      <div className="navbar-left">
        <Link to="/" className="logo">
          <img src="/logo192.png" alt="Symphoni Logo" className="logo-image" />
          <span className="app-title">Symphoni</span>
        </Link>
      </div>
      {currentUser && (
        <div className="navbar-center">
          <Link className="nav-item" to="/instruct-schemas">Instruct Schemas</Link>
          <Link className="nav-item" to="/my-arrays">My Arrays</Link>
          <Link className="nav-item" to="/past-is-threads">Past IS-Threads</Link>
          <Link className="nav-item" to="/is-setup">IS-Setup</Link>
          <Link className="nav-item" to="/">Persona-Setup</Link>
          <Link className="nav-item" to="/tools">Tools</Link>
        </div>
      )}
      <div className="navbar-right">
        {currentUser ? (
          <>
            <FaUserCircle size={24} className="profile-icon" />
            <button className="logout-button" onClick={handleLogout}>Logout</button>
          </>
        ) : (
          <>
            <Link to="/login" className="auth-link">Login</Link>
            <Link to="/signup" className="auth-link">Sign Up</Link>
          </>
        )}
      </div>
    </div>
  );
}

export default Navbar;
