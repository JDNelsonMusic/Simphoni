// src/components/PersonaSetup.js
import React from 'react';
import ModelModule from './ModelModule';
import PersonaLine from './PersonaLine';
import HeaderButtons from './HeaderButtons';
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

function PersonaSetup({ setCurrentPage, personas, setPersonas }) {
  const updatePersona = (index, updatedPersona) => {
    const newPersonas = [...personas];
    newPersonas[index] = updatedPersona;
    setPersonas(newPersonas);
  };

  const savePersonaArray = () => {
    console.log("Persona array saved", personas);
    alert("Persona array saved successfully!");
    // Implement saving logic here (e.g., save to local storage or backend)
  };

  return (
    <div className="persona-setup">
      <HeaderButtons
        mainButtonLabel="CONTINUE TO INSTRUCT SETUP"
        mainButtonColor="#1E90FF"
        secondaryButtonLabel="SAVE PERSONA ARRAY"
        savePersonaArray={savePersonaArray}
        setCurrentPage={setCurrentPage}
        nextPage="ISSetup"
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
            key={index}
            index={index}
            persona={persona}
            updatePersona={updatePersona}
          />
        ))}
      </div>
    </div>
  );
}

export default PersonaSetup;
