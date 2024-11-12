import React, { useState } from 'react';
import HeaderButtons from './HeaderButtons';
import ModelModule from './ModelModule';
import PersonaLine from './PersonaLine';
import './PersonaSetup.css';

const PersonaSetup = () => {
  const models = [
    'llama3.2:3b', 'mistral-nemo', 'stable-code', 'smol-m13b', 'orca-mini-70b',
    'stable-diffusion', 'falcon-7b', 'nous-hermes-34b', 'smol-m21-5m',
    'gpt4all', 'open-assistant', 'mistral-7b', 'vicuna-13b', 'alpaca-7b',
    'gpt-neo-2.7b', 'bloom-560m', 'cerebras-111m'
  ];

  const [personas, setPersonas] = useState(Array(9).fill({
    nickname: '',
    model: 'llama3.2:3b',
    creativity: 5,
  }));

  const savePersonaArray = () => {
    console.log("Persona array saved", personas);
    alert("Persona array saved successfully!");
  };

  return (
    <div className="persona-setup">
      <HeaderButtons savePersonaArray={savePersonaArray} />
      <h2>Persona Setup</h2>
      <div className="model-modules">
        {models.map((model, index) => (
          <ModelModule key={index} model={model} />
        ))}
      </div>
      <div className="persona-lines">
        {personas.map((persona, index) => (
          <PersonaLine key={index} index={index} persona={persona} />
        ))}
      </div>
    </div>
  );
};

export default PersonaSetup;
