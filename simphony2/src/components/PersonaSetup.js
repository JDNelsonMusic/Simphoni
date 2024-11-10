// src/components/PersonaSetup.js
import React, { useState, useEffect, useRef } from 'react';
import ModelModule from './ModelModule';
import PersonaLine from './PersonaLine';
import HeaderButtons from './HeaderButtons';
import { DndProvider } from 'react-dnd';
import { HTML5Backend } from 'react-dnd-html5-backend';
import { useNavigate } from 'react-router-dom';
import './PersonaSetup.css';

// Define available models
const available_models = [
  { name: 'llama3.2:1b', display: 'llama3.2:1b' },
  { name: 'llama3.2:3b', display: 'llama3.2:3b' },
  { name: 'mistral:7b', display: 'mistral:7b' },
  { name: 'mistral-nemo', display: 'mistral-nemo' },
  { name: 'solar-pro', display: 'solar-pro' },
  { name: 'stable-code', display: 'stable-code' },
  { name: 'nous-hermes:34b', display: 'nous-hermes:34b' },
  { name: 'Stable-Diffusion:3.5b', display: 'Stable-Diffusion:3.5b' },
  { name: 'phi3:14b-medium-128k-instruct-fp16', display: 'phi3:14b-medium-128k-instruct-fp16' },
  { name: 'llama3.1:70b', display: 'llama3.1:70b' },
  { name: 'orca-mini:70b', display: 'orca-mini:70b' },
  { name: 'nemotron:70b', display: 'nemotron:70b' },
  { name: 'phi3:medium-128k', display: 'phi3:medium-128k' },
  { name: 'falcon:7b', display: 'falcon:7b' },
  { name: 'wizard-vicuna-uncensored:30b', display: 'wizard-vicuna-uncensored:30b' },
  { name: 'smolm2:135m', display: 'smolm2:135m' },
  { name: 'smolm2:1.7b', display: 'smolm2:1.7b' }
];

function PersonaSetup() {
  const navigate = useNavigate();
  const [personas, setPersonas] = useState([]);
  const [arrayName, setArrayName] = useState('');
  const fileInputRef = useRef(null);

  useEffect(() => {
    // Initialize personas locally
    const initialPersonas = Array.from({ length: 9 }, (_, index) => ({
      id: `${Date.now()}_${index}`, // Unique ID
      nickname: '',
      model: '',
      creativity: 5,
      definePersona: '',
    }));
    setPersonas(initialPersonas);
    console.log('Initialized personas:', initialPersonas);
  }, []);

  // Function to update a specific persona
  const updatePersona = (index, updatedPersona) => {
    const newPersonas = [...personas];
    newPersonas[index] = { ...newPersonas[index], ...updatedPersona };
    setPersonas(newPersonas);
    console.log(`Updated persona ${index + 1}:`, newPersonas[index]);
  };

  // Function to reset a persona
  const removePersona = (index) => {
    const newPersonas = [...personas];
    newPersonas[index] = {
      id: `${Date.now()}_${index}`,
      nickname: '',
      model: '',
      creativity: 5,
      definePersona: '',
    };
    setPersonas(newPersonas);
    console.log(`Reset persona ${index + 1}`);
  };

  // Function to save persona array as JSON file
  const savePersonaArray = () => {
    if (!arrayName.trim()) {
      alert('Please enter a name for the persona array before saving.');
      return;
    }

    const data = {
      arrayName,
      personas
    };

    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);

    const link = document.createElement('a');
    link.href = url;
    link.download = `persona-array:${arrayName}.json`;
    link.click();

    URL.revokeObjectURL(url);
    console.log('Persona array saved:', data);
  };

  // Function to load persona array from JSON file
  const loadPersonaArray = (event) => {
    const file = event.target.files[0];
    if (!file) {
      return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const data = JSON.parse(e.target.result);
        if (data.personas && Array.isArray(data.personas)) {
          setPersonas(data.personas);
          setArrayName(data.arrayName || '');
          console.log('Persona array loaded:', data);
        } else {
          alert('Invalid persona array file.');
        }
      } catch (error) {
        console.error('Error parsing persona array file:', error);
        alert('Failed to load persona array file.');
      }
    };
    reader.readAsText(file);
  };

  // Function to trigger file input click
  const triggerFileInput = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  // Function to navigate to IS:Setup page with persona data
  const startSetup = () => {
    if (!arrayName.trim()) {
      alert('Please enter a name for the persona array before continuing.');
      return;
    }
    navigate('/is-setup', { state: { personas, arrayName } });
    console.log('Navigated to IS:Setup with personas:', personas);
  };

  return (
    <DndProvider backend={HTML5Backend}>
      <div className="persona-setup">
        <HeaderButtons
          mainButtonLabel="CONTINUE TO INSTRUCT SETUP"
          mainButtonColor="#1E90FF"
          secondaryButtonLabel="SAVE PERSONA ARRAY"
          onSecondaryButtonClick={savePersonaArray} // Updated prop name
          setCurrentPage={startSetup} // Navigates to '/is-setup'
          nextPage="/is-setup" // Optional, can be removed if not used
          pageTitle="Persona Array"
        />
        <div className="persona-array-name">
          <label htmlFor="arrayName">Persona Array Name:</label>
          <input
            type="text"
            id="arrayName"
            value={arrayName}
            onChange={(e) => setArrayName(e.target.value)}
            placeholder="Enter persona array name"
            className="array-name-input"
          />
        </div>
        <div className="save-load-buttons">
          <button onClick={savePersonaArray} className="save-button">
            Save Persona Array
          </button>
          <button onClick={triggerFileInput} className="load-button">
            Load Persona Array
          </button>
          <input
            type="file"
            accept="application/json"
            ref={fileInputRef}
            onChange={loadPersonaArray}
            style={{ display: 'none' }}
          />
        </div>
        <div className="model-modules">
          {available_models.map((model, index) => (
            <ModelModule key={index} model={model} />
          ))}
        </div>
        <div className="persona-lines">
          {personas.map((persona, index) => (
            <PersonaLine
              key={persona.id}
              index={index}
              persona={persona}
              updatePersona={updatePersona}
              removePersona={() => removePersona(index)}
            />
          ))}
        </div>
      </div>
    </DndProvider>
  );
}

export default PersonaSetup;
