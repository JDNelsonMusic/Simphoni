// src/components/PersonaSetup.js
import React, { useState, useEffect } from 'react';
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
  { name: 'smolm2:1.7b', display: 'smolm2:1.7b' },
];

function PersonaSetup() {
  const navigate = useNavigate();
  const [personas, setPersonas] = useState([]);

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
  };

  // Function to navigate to IS:Setup page
  const startSetup = () => {
    navigate('/is-setup');
  };

  return (
    <DndProvider backend={HTML5Backend}>
      <div className="persona-setup">
        <HeaderButtons
          mainButtonLabel="CONTINUE TO INSTRUCT SETUP"
          mainButtonColor="#1E90FF"
          secondaryButtonLabel="SAVE PERSONA ARRAY"
          savePersonaArray={() => alert('Persona Array is automatically saved.')}
          setCurrentPage={startSetup} // Navigates to '/is-setup'
          nextPage="/is-setup" // Optional, can be removed if not used
          pageTitle="Persona Array"
        />
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
