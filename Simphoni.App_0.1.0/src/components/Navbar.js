// src/components/Navbar.js
import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
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
        <NavLink to="/" className="logo">
          <img src="/logo192.png" alt="Symphoni Logo" className="logo-image" />
          <span className="app-title">Symphoni</span>
        </NavLink>
      </div>
      {currentUser && (
        <div className="navbar-center">
          <NavLink
            to="/persona-setup"
            className={({ isActive }) => (isActive ? 'nav-item active-nav-item' : 'nav-item')}
          >
            Persona Setup
          </NavLink>
          <NavLink
            to="/is-setup"
            className={({ isActive }) => (isActive ? 'nav-item active-nav-item' : 'nav-item')}
          >
            IS Setup
          </NavLink>
          <NavLink
            to="/instruct-schemas"
            className={({ isActive }) => (isActive ? 'nav-item' : 'nav-item')}
          >
            Instruct Schemas
          </NavLink>
          <NavLink
            to="/my-arrays"
            className={({ isActive }) => (isActive ? 'nav-item' : 'nav-item')}
          >
            My Arrays
          </NavLink>
          <NavLink
            to="/past-is-threads"
            className={({ isActive }) => (isActive ? 'nav-item' : 'nav-item')}
          >
            Past IS-Threads
          </NavLink>
          <NavLink
            to="/tools"
            className={({ isActive }) => (isActive ? 'nav-item' : 'nav-item')}
          >
            Tools
          </NavLink>
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
            <NavLink to="/login" className="auth-link">Login</NavLink>
            <NavLink to="/signup" className="auth-link">Sign Up</NavLink>
          </>
        )}
      </div>
    </div>
  );
}

export default Navbar;
