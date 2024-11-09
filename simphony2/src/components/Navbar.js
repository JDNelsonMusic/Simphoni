// src/components/Navbar.js
import React from 'react';
import './Navbar.css';
import { FaUserCircle } from 'react-icons/fa';

function Navbar({ setCurrentPage }) {
  return (
    <div className="navbar">
      <div className="navbar-left">
        <div className="logo" onClick={() => setCurrentPage('PersonaSetup')}>
          <img src="/logo192.png" alt="Symphoni Logo" className="logo-image" />
          <span className="app-title">Symphoni</span>
        </div>
      </div>
      <div className="navbar-center">
        <span className="nav-item" onClick={() => setCurrentPage('InstructSchemas')}>Instruct Schemas</span>
        <span className="nav-item" onClick={() => setCurrentPage('MyArrays')}>My Arrays</span>
        <span className="nav-item" onClick={() => setCurrentPage('PastISThreads')}>Past IS-Threads</span>
        <span className="nav-item" onClick={() => setCurrentPage('ISSetup')}>IS-Setup</span>
        <span className="nav-item" onClick={() => setCurrentPage('PersonaSetup')}>Persona-Setup</span>
        <span className="nav-item" onClick={() => setCurrentPage('Tools')}>Tools</span>
      </div>
      <div className="navbar-right">
        <FaUserCircle size={24} onClick={() => alert('Go to Dashboard')} className="profile-icon" />
      </div>
    </div>
  );
}

export default Navbar;
