// src/components/InstructLine.js
import React from 'react';
import { useDrop } from 'react-dnd';
import { FaSave } from 'react-icons/fa';
import './InstructLine.css';

function InstructLine({ index, data, updateInstructLine }) {
  const [{ isOver }, drop] = useDrop({
    accept: 'persona',
    drop: (item) => updateInstructLine(index, { persona: item.persona }),
    collect: (monitor) => ({
      isOver: !!monitor.isOver(),
    }),
  });

  const handleInputChange = (e) => {
    updateInstructLine(index, { instructText: e.target.value });
  };

  const handleToolChange = (e) => {
    updateInstructLine(index, { tool: e.target.value });
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file && file.size <= 5 * 1024 * 1024) { // 5MB limit
      updateInstructLine(index, { file });
    } else {
      alert("Please upload a file smaller than 5MB.");
    }
  };

  const savePersona = () => {
    updateInstructLine(index, {
      nickname: data.nickname,
      creativity: data.creativity,
      model: data.model,
      definePersona: data.definePersona,
    });
    alert(`Instruct Line ${index + 1} saved!`);
  };

  return (
    <div className="instruct-line">
      <input
        type="file"
        accept=".png,.txt"
        onChange={handleFileChange}
        className="file-upload"
      />
      <select onChange={handleToolChange} className="tool-selection">
        <option value="">Select Tool</option>
        <option value="web-search insert">Web-Search Insert</option>
        <option value="screenshot-timer">Screenshot Timer</option>
        <option value="proaction trigger">Proaction Trigger</option>
      </select>
      <textarea
        value={data.instructText}
        onChange={handleInputChange}
        placeholder={`Instruct ${index + 1}`}
        className="instruct-field"
        style={{ height: 'auto', width: '1200px' }}
      />
      <div
        className="persona-slot"
        ref={drop}
        style={{ backgroundColor: isOver ? '#4A0078' : '#2A0036' }}
      >
        {data.persona ? data.persona.nickname : 'Drop Persona Here'}
      </div>
      <button className="inference-number">{index + 1}</button>
      <FaSave className="save-icon" onClick={savePersona} />
    </div>
  );
}

export default InstructLine;
