// src/components/ActivePersonas.js
import React from 'react';
import './ActivePersonas.css';

function ActivePersonas({ personas }) {
  return (
    <div className="active-personas">
      <h3>Active Personas:</h3>
      <div className="active-personas-list">
        {personas.map((persona, index) => (
          <div key={index} className="active-persona-module">
            {persona.model || 'No Model Assigned'}
          </div>
        ))}
      </div>
    </div>
  );
}

export default ActivePersonas;
