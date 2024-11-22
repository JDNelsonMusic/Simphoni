// src/components/ISSetup.js
import React, { useState, useEffect, useRef } from 'react';
import HeaderButtons from './HeaderButtons';
import ActivePersonas from './ActivePersonas';
import InstructLine from './InstructLine';
import LoopSegment from './LoopSegment'; // Ensure this component exists
import { useAuth } from './AuthProvider';
import { useNavigate, useLocation } from 'react-router-dom';
import { firestore } from '../firebase'; // Updated import
import { collection, addDoc, getDocs } from 'firebase/firestore'; // Import necessary Firestore functions
import { DndProvider, useDrop } from 'react-dnd';
import { HTML5Backend } from 'react-dnd-html5-backend';
import './ISSetup.css';

function ISSetup() {
  const { currentUser } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [instructLines, setInstructLines] = useState([]);
  const [loading, setLoading] = useState(true);
  const [arrayName, setArrayName] = useState('');
  const [personas, setPersonas] = useState([]);
  const fileInputRef = useRef(null);

  // Receive persona data from navigation state or Firebase
  useEffect(() => {
    if (!currentUser) {
      alert('You must be logged in to access this page.');
      navigate('/login'); // Redirect to login page
      return;
    }

    const { personas: loadedPersonas, arrayName: loadedArrayName } = location.state || { personas: [], arrayName: '' };

    if (loadedPersonas.length === 0 && loadedArrayName === '') {
      alert('No Persona Array data received. Please set up your personas first.');
      navigate('/persona-setup'); // Redirect to PersonaSetup
      return;
    }

    setPersonas(loadedPersonas);
    setArrayName(loadedArrayName);

    // Initialize instructLines with default or loaded data
    const initialInstructLines = loadedPersonas.map((persona, index) => ({
      id: index,
      type: 'instruct', // 'instruct' or 'loop'
      content: '',
      persona: persona.nickname || '',
      tool: '',
      file: null,
    }));

    setInstructLines(initialInstructLines);
    setLoading(false);
    console.log('Loaded personas and initialized instruct lines:', loadedPersonas, initialInstructLines);
  }, [currentUser, location.state, navigate]);

  // Function to update an instruct line
  const updateInstructLine = (index, data) => {
    const newInstructLines = [...instructLines];
    newInstructLines[index] = { ...newInstructLines[index], ...data };
    setInstructLines(newInstructLines);
    console.log(`Updated instruct line ${index + 1}:`, newInstructLines[index]);
  };

  // Function to add a new instruct line
  const addInstructLine = () => {
    const newInstructLine = {
      id: instructLines.length,
      type: 'instruct',
      content: '',
      persona: '',
      tool: '',
      file: null,
    };
    setInstructLines([...instructLines, newInstructLine]);
    console.log('Added new instruct line:', newInstructLine);
  };

  // Function to add a loop segment
  const addLoopSegment = () => {
    const newLoop = {
      id: instructLines.length,
      type: 'loop',
      iterations: 2, // default
      instructLines: [],
    };
    setInstructLines([...instructLines, newLoop]);
    console.log('Added new loop segment:', newLoop);
  };

  // Function to save instruct schema to Firebase
  const saveInstructSchema = async () => {
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
      createdAt: new Date(),
    };

    try {
      await addDoc(collection(firestore, 'instructSchemas'), data);
      alert('Instruct schema saved to Firebase successfully.');
      console.log('Instruct schema saved to Firebase:', data);
    } catch (error) {
      console.error('Error saving instruct schema to Firebase:', error);
      alert('Failed to save instruct schema.');
    }
  };

  // Function to load instruct schema from Firebase
  const loadInstructSchema = async () => {
    try {
      const querySnapshot = await getDocs(collection(firestore, 'instructSchemas'));
      if (querySnapshot.empty) {
        alert('No instruct schemas found.');
        return;
      }

      const schemas = [];
      querySnapshot.forEach((doc) => {
        schemas.push({ id: doc.id, ...doc.data() });
      });

      // Let the user select which schema to load
      const schemaNames = schemas.map((schema, index) => `${index + 1}. ${schema.schemaName}`);
      const selection = prompt(`Select a schema to load:\n${schemaNames.join('\n')}`);
      const selectedIndex = parseInt(selection, 10) - 1;

      if (isNaN(selectedIndex) || selectedIndex < 0 || selectedIndex >= schemas.length) {
        alert('Invalid selection.');
        return;
      }

      const selectedSchema = schemas[selectedIndex];
      setInstructLines(selectedSchema.instructLines);
      setArrayName(selectedSchema.arrayName);
      setPersonas(selectedSchema.personas);
      alert(`Loaded schema: ${selectedSchema.schemaName}`);
      console.log('Loaded instruct schema from Firebase:', selectedSchema);
    } catch (error) {
      console.error('Error loading instruct schema from Firebase:', error);
      alert('Failed to load instruct schema.');
    }
  };

  // Function to handle drag-and-drop
  const [{ isOver }, drop] = useDrop(() => ({
    accept: 'MODEL',
    drop: (item) => handleDrop(item),
    collect: (monitor) => ({
      isOver: !!monitor.isOver(),
    }),
  }), [instructLines]);

  const handleDrop = (item) => {
    // Add a new instruct line with the dropped model
    const newInstructLine = {
      id: instructLines.length,
      type: 'instruct',
      content: '',
      persona: item.nickname || '',
      tool: item.modelName || '',
      file: null,
    };
    setInstructLines([...instructLines, newInstructLine]);
    console.log('Dropped model:', item, 'Added instruct line:', newInstructLine);
  };

  if (loading) {
    return <div className="loading">Loading IS:Setup...</div>;
  }

  return (
    <DndProvider backend={HTML5Backend}>
      <div className="is-setup">
        <HeaderButtons
          mainButtonLabel="START SEQUENCE"
          mainButtonColor="#FF007C"
          secondaryButtonLabel="SAVE INSTRUCT SCHEMA"
          onSecondaryButtonClick={saveInstructSchema} // Save schema to Firebase
          setCurrentPage={() => navigate('/is-thread')} // Navigate to IS:Thread
          nextPage="/is-thread" // Optional
          pageTitle={`Instruct Sequence Setup - ${arrayName}`}
        />
        <div className="load-schema-buttons">
          <button onClick={loadInstructSchema} className="load-schema-button">
            LOAD SCHEMA
          </button>
        </div>
        <div className="model-modules">
          {/* Display all model modules, including personas and custom GPT models */}
          {personas.map((persona, index) => (
            <div key={index} className="model-module">
              <strong>{persona.nickname}</strong>: {persona.model}
            </div>
          ))}
          {/* Custom GPT models */}
          <div className="model-module">KEE1:txt</div>
          <div className="model-module">KEE1:web</div>
          <div className="model-module">KEE1:img</div>
          <div className="model-module">KEE1:vid</div>
          <div className="model-module">KEE1:code</div>
          {/* Add more models as needed */}
        </div>
        <div className="instruct-lines" ref={drop} style={{ backgroundColor: isOver ? '#e0e0e0' : '#1E034A' }}>
          {instructLines.map((line, index) => (
            line.type === 'instruct' ? (
              <InstructLine
                key={line.id}
                index={index}
                data={line}
                updateInstructLine={updateInstructLine}
              />
            ) : (
              <LoopSegment
                key={line.id}
                index={index}
                data={line}
                updateInstructLine={updateInstructLine}
              />
            )
          ))}
          <div className="add-buttons">
            <button onClick={addInstructLine} className="add-button">Add Instruct Line</button>
            <button onClick={addLoopSegment} className="add-button">Add Loop Segment</button>
          </div>
        </div>
      </div>
    </DndProvider>
  );
}

export default ISSetup;
