// src/components/ActivePersonas.js
import React from 'react';
import './ActivePersonas.css';

function ActivePersonas({ personas, arrayName }) {
  return (
    <div className="active-personas">
      <h3>Active Personas for "{arrayName}":</h3>
      <div className="active-personas-list">
        {personas.map((persona, index) => (
          <div key={index} className="active-persona-module">
            <strong>Persona {index + 1}:</strong> {persona.model || 'No Model Assigned'}
          </div>
        ))}
      </div>
    </div>
  );
}

export default ActivePersonas;
