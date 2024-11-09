import React from 'react';
import './Navbar.css';

function Navbar() {
  return (
    <div className="navbar">
      <div className="logo">Symphoni</div>
      <div className="nav-items">
        <span>Instruct Schemas</span>
        <span>My Arrays</span>
        <span>Past IS-Threads</span>
        <span>IS-Setup</span>
        <span>Persona-Setup</span>
        <span>Tools</span>
      </div>
      <div className="profile-icon">Profile</div>
    </div>
  );
}

export default Navbar;
