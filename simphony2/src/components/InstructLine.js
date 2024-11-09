// src/components/InstructLine.js
import React, { useState } from 'react';
import './InstructLine.css';

function InstructLine({ index, data, updateInstructLine }) {
  const [instructText, setInstructText] = useState(data.instructText || '');
  const [persona, setPersona] = useState(data.persona || '');
  const [tool, setTool] = useState(data.tool || '');
  const [file, setFile] = useState(data.file || null);

  const handleChange = (e) => {
    const { name, value, files } = e.target;
    if (name === 'instructText') setInstructText(value);
    if (name === 'persona') setPersona(value);
    if (name === 'tool') setTool(value);
    if (name === 'file') setFile(files[0]);
  };

  const saveInstructLine = () => {
    updateInstructLine(index, {
      instructText,
      persona,
      tool,
      file,
    });
    alert(`Instruct Line ${index + 1} saved!`);
  };

  return (
    <div className="instruct-line">
      <textarea
        name="instructText"
        value={instructText}
        onChange={(e) => setInstructText(e.target.value)}
        placeholder="Instruct Text"
        className="instruct-textarea"
      />
      <input
        type="text"
        name="persona"
        value={persona}
        onChange={(e) => setPersona(e.target.value)}
        placeholder="Persona"
        className="persona-input"
      />
      <input
        type="text"
        name="tool"
        value={tool}
        onChange={(e) => setTool(e.target.value)}
        placeholder="Tool"
        className="tool-input"
      />
      <input
        type="file"
        name="file"
        onChange={handleChange}
        className="file-input"
      />
      <button className="save-instruct-line-button" onClick={saveInstructLine}>
        Save Instruct Line
      </button>
    </div>
  );
}

export default InstructLine;
