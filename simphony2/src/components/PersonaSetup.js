// src/components/PersonaSetup.js
import React, { useState, useEffect } from 'react';
import ModelModule from './ModelModule';
import PersonaLine from './PersonaLine';
import HeaderButtons from './HeaderButtons';
import { firestore } from '../firebase';
import { useAuth } from './AuthProvider';
import { DndProvider } from 'react-dnd';
import { HTML5Backend } from 'react-dnd-html5-backend';
import './PersonaSetup.css';

const available_models = [
  { 'name': 'llama3.2:1b', 'display': 'llama3.2:1b' },
  { 'name': 'llama3.2:3b', 'display': 'llama3.2:3b' },
  { 'name': 'mistral:7b', 'display': 'mistral:7b' },
  { 'name': 'mistral-nemo', 'display': 'mistral-nemo' },
  { 'name': 'solar-pro', 'display': 'solar-pro' },
  { 'name': 'stable-code', 'display': 'stable-code' },
  { 'name': 'nous-hermes:34b', 'display': 'nous-hermes:34b' },
  { 'name': 'Stable-Diffusion:3.5b', 'display': 'Stable-Diffusion:3.5b' },
  { 'name': 'phi3:14b-medium-128k-instruct-fp16', 'display': 'phi3:14b-medium-128k-instruct-fp16' },
  { 'name': 'llama3.1:70b', 'display': 'llama3.1:70b' },
  { 'name': 'orca-mini:70b', 'display': 'orca-mini:70b' },
  { 'name': 'nemotron:70b', 'display': 'nemotron:70b' },
  { 'name': 'phi3:medium-128k', 'display': 'phi3:medium-128k' },
  { 'name': 'falcon:7b', 'display': 'falcon:7b' },
  { 'name': 'wizard-vicuna-uncensored:30b', 'display': 'wizard-vicuna-uncensored:30b' },
  { 'name': 'smolm2:135m', 'display': 'smolm2:135m' },
  { 'name': 'smolm2:1.7b', 'display': 'smolm2:1.7b' }
];

function PersonaSetup() {
  const { currentUser } = useAuth();
  const [personas, setPersonas] = useState([]);

  const updatePersona = (index, updatedPersona) => {
    const newPersonas = [...personas];
    newPersonas[index] = updatedPersona;
    setPersonas(newPersonas);
  };

  const addPersona = () => {
    const newPersona = {
      id: Date.now(), // Unique ID based on timestamp
      nickname: '',
      model: '',
      creativity: 0.5,
      definePersona: '',
    };
    setPersonas([...personas, newPersona]);
  };

  const removePersona = (index) => {
    const newPersonas = personas.filter((_, i) => i !== index);
    setPersonas(newPersonas);
  };

  const savePersonaArray = async () => {
    const arrayName = prompt('Enter a name for this Persona Array:');
    if (!arrayName) {
      alert('Array name is required.');
      return;
    }

    const newArray = {
      name: arrayName,
      owner: currentUser.uid,
      access: 'Private', // Default access level
      allowedUsers: [],
      personas: personas.map((p) => ({
        nickname: p.nickname,
        model: p.model,
        creativity: p.creativity,
        definePersona: p.definePersona,
      })),
      timestamp: new Date(),
    };

    try {
      await firestore.collection('personaArrays').add(newArray);
      alert('Persona Array saved successfully!');
    } catch (error) {
      console.error('Error saving Persona Array: ', error);
      alert('Failed to save Persona Array.');
    }
  };

  return (
    <DndProvider backend={HTML5Backend}>
      <div className="persona-setup">
        <HeaderButtons
          mainButtonLabel="CONTINUE TO INSTRUCT SETUP"
          mainButtonColor="#1E90FF"
          secondaryButtonLabel="SAVE PERSONA ARRAY"
          savePersonaArray={savePersonaArray}
          setCurrentPage={() => {}}
          nextPage="/is-setup"
          pageTitle="Persona Array"
        />
        <div className="model-modules">
          {available_models.map((model, index) => (
            <ModelModule key={index} model={model} />
          ))}
        </div>
        <button className="add-persona-button" onClick={addPersona}>
          Add Persona
        </button>
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
