// src/components/ISSetup.js
import React, { useState, useEffect } from 'react';
import HeaderButtons from './HeaderButtons';
import ActivePersonas from './ActivePersonas';
import InstructLine from './InstructLine';
import { useAuth } from './AuthProvider';
import { useNavigate, useLocation } from 'react-router-dom';
import './ISSetup.css';

function ISSetup() {
  const { currentUser } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [instructLines, setInstructLines] = useState([]);
  const [loading, setLoading] = useState(true);
  
  // Receive persona data from navigation state
  const { personas, arrayName } = location.state || { personas: [], arrayName: '' };

  useEffect(() => {
    if (!currentUser) {
      alert('You must be logged in to access this page.');
      navigate('/login'); // Redirect to login page
      return;
    }

    if (!personas.length) {
      alert('No Persona Array data received. Please set up your personas first.');
      navigate('/persona-setup'); // Redirect to PersonaSetup
      return;
    }

    // Initialize instructLines with nine instruct lines
    const initialInstructLines = Array.from({ length: 9 }, (_, index) => ({
      id: index,
      instructText: '',
      persona: '', // Placeholder for assigned persona
      tool: '',
      file: null,
    }));
    setInstructLines(initialInstructLines);
    setLoading(false);
    console.log('Received personas:', personas);
  }, [currentUser, personas, navigate]);

  const handleNumLinesChange = (e) => {
    const newNum = parseInt(e.target.value, 10) || 0;
    const updatedInstructLines = Array.from({ length: newNum }, (_, index) => ({
      id: index,
      instructText: '',
      persona: '', // Placeholder for assigned persona
      tool: '',
      file: null,
    }));
    setInstructLines(updatedInstructLines);
  };

  const updateInstructLine = (index, data) => {
    const newInstructLines = [...instructLines];
    newInstructLines[index] = { ...newInstructLines[index], ...data };
    setInstructLines(newInstructLines);
  };

  // Function to save instruct schema as JSON file
  const saveInstructSchema = () => {
    const schemaName = prompt('Enter a name for the instruct schema:');
    if (!schemaName) {
      alert('Schema name is required.');
      return;
    }

    const data = {
      schemaName,
      instructLines,
      arrayName,
      personas,
    };

    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);

    const link = document.createElement('a');
    link.href = url;
    link.download = `instruct-schema:${schemaName}.json`;
    link.click();

    URL.revokeObjectURL(url);
    console.log('Instruct schema saved:', data);
  };

  // Function to save instruct schema via HeaderButtons
  const saveInstructSchemaViaHeader = () => {
    saveInstructSchema();
  };

  // Function to navigate to ISThread page
  const startSequence = () => {
    // Implement navigation to ISThread or execution logic
    navigate('/is-thread');
  };

  if (loading) {
    return <div className="loading">Loading IS:Setup...</div>;
  }

  return (
    <div className="is-setup">
      <HeaderButtons
        mainButtonLabel="START SEQUENCE"
        mainButtonColor="#FF007C"
        secondaryButtonLabel="SAVE INSTRUCT SCHEMA"
        onSecondaryButtonClick={saveInstructSchemaViaHeader} // Updated prop name
        setCurrentPage={startSequence} // Navigates to '/is-thread'
        nextPage="/is-thread" // Optional, can be removed if not used
        pageTitle={`Instruct Sequence Setup - ${arrayName}`}
      />
      <div className="num-lines-input">
        <label>Number of Instruct Lines:</label>
        <input
          type="number"
          value={instructLines.length}
          onChange={handleNumLinesChange}
          min="1"
          max="20" // Set a reasonable max limit
        />
      </div>
      <ActivePersonas personas={personas} arrayName={arrayName} />
      <div className="instruct-lines">
        {instructLines.map((line, index) => (
          <InstructLine
            key={line.id}
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
