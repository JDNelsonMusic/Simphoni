// src/components/LoopSegment.js
import React, { useState } from 'react';
import InstructLine from './InstructLine';
import './LoopSegment.css';

function LoopSegment({ index, data, updateInstructLine }) {
  const [iterations, setIterations] = useState(data.iterations || 2);
  const [loopInstructLines, setLoopInstructLines] = useState(data.instructLines || []);

  const handleIterationChange = (e) => {
    const value = parseInt(e.target.value, 10) || 1;
    setIterations(value);
    updateInstructLine(index, { iterations: value, instructLines: loopInstructLines });
  };

  const handleLoopInstructLineChange = (loopIndex, updatedData) => {
    const newLoopInstructLines = [...loopInstructLines];
    newLoopInstructLines[loopIndex] = { ...newLoopInstructLines[loopIndex], ...updatedData };
    setLoopInstructLines(newLoopInstructLines);
    updateInstructLine(index, { instructLines: newLoopInstructLines });
  };

  const addLoopInstructLine = () => {
    const newLine = {
      id: loopInstructLines.length,
      instructText: '',
      persona: '',
      tool: '',
      file: null,
    };
    setLoopInstructLines([...loopInstructLines, newLine]);
    updateInstructLine(index, { instructLines: [...loopInstructLines, newLine] });
  };

  return (
    <div className="loop-segment">
      <div className="loop-header">
        <label>Loop Iterations:</label>
        <input
          type="number"
          value={iterations}
          onChange={handleIterationChange}
          min="1"
          className="loop-iteration-input"
        />
      </div>
      <div className="loop-instruct-lines">
        {loopInstructLines.map((line, loopIndex) => (
          <InstructLine
            key={loopIndex}
            index={loopIndex}
            data={line}
            updateInstructLine={(updatedData) => handleLoopInstructLineChange(loopIndex, updatedData)}
          />
        ))}
        <button onClick={addLoopInstructLine} className="add-loop-line-button">
          Add Loop Instruct Line
        </button>
      </div>
    </div>
  );
}

export default LoopSegment;
