// src/components/PersonaModule.js
import React from 'react';
import { useDrag } from 'react-dnd';
import './PersonaModule.css';

function PersonaModule({ persona }) {
  const [{ isDragging }, drag] = useDrag(() => ({
    type: 'persona',
    item: { persona },
    collect: (monitor) => ({
      isDragging: !!monitor.isDragging(),
    }),
  }), [persona]);

  return (
    <div
      className="persona-module"
      ref={drag}
      style={{ opacity: isDragging ? 0.5 : 1 }}
    >
      {persona.nickname || 'Unnamed Persona'}
    </div>
  );
}

export default PersonaModule;
