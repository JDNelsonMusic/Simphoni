// src/components/ISSetup.js
import React, { useState } from 'react';
import HeaderButtons from './HeaderButtons';
import ActivePersonas from './ActivePersonas';
import InstructLine from './InstructLine';
import './ISSetup.css';

function ISSetup({ setCurrentPage, personas }) {
  // State for the number of instruct lines
  const [numInstructLines, setNumInstructLines] = useState(6);

  // State for the instruct lines data
  const [instructLines, setInstructLines] = useState(
    Array(6).fill().map((_, index) => ({
      id: index,
      instructText: '',
      persona: null,
      tool: '',
      file: null,
    }))
  );

  // Function to handle the number of instruct lines
  const handleNumLinesChange = (e) => {
    const newNum = parseInt(e.target.value, 10) || 0;
    setNumInstructLines(newNum);
    setInstructLines(
      Array(newNum).fill().map((_, index) => ({
        id: index,
        instructText: '',
        persona: null,
        tool: '',
        file: null,
      }))
    );
  };

  // Function to update an instruct line
  const updateInstructLine = (index, data) => {
    const newInstructLines = [...instructLines];
    newInstructLines[index] = { ...newInstructLines[index], ...data };
    setInstructLines(newInstructLines);
  };

  const saveInstructSequence = () => {
    console.log("Instruct sequence saved", instructLines);
    alert("Instruct sequence saved successfully!");
    // Implement saving logic here
  };

  const startSequence = () => {
    console.log("Starting sequence with", instructLines);
    alert("Sequence started!");
    // Implement sequence start logic here
  };

  return (
    <div className="is-setup">
      <HeaderButtons
        mainButtonLabel="START SEQUENCE"
        mainButtonColor="#FF007C"
        secondaryButtonLabel="SAVE NEW INSTRUCT SEQUENCE"
        savePersonaArray={saveInstructSequence}
        setCurrentPage={setCurrentPage}
        nextPage="ISThread" // Adjust as needed
        pageTitle="Instruct Sequence Setup"
      />
      <div className="num-lines-input">
        <label>Number of Instruct Lines:</label>
        <input
          type="number"
          value={numInstructLines}
          onChange={handleNumLinesChange}
          min="1"
        />
      </div>
      <ActivePersonas personas={personas} />
      <div className="instruct-lines">
        {instructLines.map((line, index) => (
          <InstructLine
            key={index}
            index={index}
            data={line}
            updateInstructLine={updateInstructLine}
          />
        ))}
      </div>
    </div>
  );
}

export default ISSetup;
