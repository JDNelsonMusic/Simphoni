// src/components/PersonaLine.js
import React, { useState } from 'react';
import { useDrop } from 'react-dnd';
import { FaSave } from 'react-icons/fa';
import './PersonaLine.css';

function PersonaLine({ index, persona, updatePersona, removePersona }) {
  const [nickname, setNickname] = useState(persona.nickname || '');
  const [creativity, setCreativity] = useState(persona.creativity || 5);
  const [model, setModel] = useState(persona.model || '');
  const [definePersona, setDefinePersona] = useState(persona.definePersona || '');

  const [{ isOver }, drop] = useDrop(() => ({
    accept: 'MODEL',
    drop: (item) => setModel(item.model.name),
    collect: (monitor) => ({
      isOver: !!monitor.isOver(),
    }),
  }), [setModel]);

  const savePersona = () => {
    updatePersona(index, {
      id: persona.id, // keep the id
      nickname,
      creativity,
      model,
      definePersona,
    });
    alert(`Persona ${index + 1} saved!`);
  };

  return (
    <div
      className="persona-line"
      ref={drop}
      style={{ backgroundColor: isOver ? '#4A0078' : '#2A0036' }}
    >
      <input
        type="text"
        value={nickname}
        onChange={(e) => setNickname(e.target.value)}
        placeholder="Nickname"
        className="nickname-input"
      />
      <div className="model-display">
        {model || 'Drag a model here'}
      </div>
      <div className="creativity-slider">
        <label>Creativity:</label>
        <input
          type="range"
          min="1"
          max="9"
          value={creativity}
          onChange={(e) => setCreativity(parseInt(e.target.value))}
        />
        <span>{creativity}</span>
      </div>
      <input
        type="text"
        value={definePersona}
        onChange={(e) => setDefinePersona(e.target.value)}
        placeholder="Define Persona"
        className="define-persona-input"
      />
      <FaSave className="save-icon" onClick={savePersona} />
      <button className="remove-persona-button" onClick={removePersona}>
        Remove
      </button>
    </div>
  );
}

export default PersonaLine;
