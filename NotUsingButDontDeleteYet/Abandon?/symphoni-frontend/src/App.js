// src/App.js
import React from 'react';
import PersonaSetup from './components/PersonaSetup';
import InstructSequenceSetup from './components/InstructSequenceSetup';
import InferenceSequence from './components/InferenceSequence';

function App() {
  return (
    <div className="min-h-screen bg-gray-900">
      <header className="bg-gray-800 p-4 text-white text-center">
        <h1 className="text-3xl">Symphoni - Inference Sequence Setup</h1>
      </header>
      <main className="p-4">
        <PersonaSetup />
        <InstructSequenceSetup />
        <InferenceSequence />
      </main>
    </div>
  );
}

export default App;
