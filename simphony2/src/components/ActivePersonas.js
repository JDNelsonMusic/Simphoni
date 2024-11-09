// src/components/ActivePersonas.js
import React from 'react';
import PersonaModule from './PersonaModule';
import './ActivePersonas.css';

function ActivePersonas({ personas }) {
  return (
    <div className="active-personas">
      {personas.map((persona, index) => (
        <PersonaModule key={index} persona={persona} />
      ))}
    </div>
  );
}

export default ActivePersonas;
