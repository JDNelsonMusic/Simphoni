// src/App.js
import React, { useState } from 'react';
import Navbar from './components/Navbar';
import PersonaSetup from './components/PersonaSetup';
import ISSetup from './components/ISSetup';
import './App.css';
import { DndProvider } from 'react-dnd';
import { HTML5Backend } from 'react-dnd-html5-backend';

function App() {
  const [currentPage, setCurrentPage] = useState('PersonaSetup');

  // State for personas
  const [personas, setPersonas] = useState(Array(9).fill().map(() => ({
    nickname: '',
    model: 'llama3.2:3b',
    creativity: 5,
    definePersona: '',
  })));

  const renderPage = () => {
    if (currentPage === 'PersonaSetup') {
      return (
        <PersonaSetup
          setCurrentPage={setCurrentPage}
          personas={personas}
          setPersonas={setPersonas}
        />
      );
    } else if (currentPage === 'ISSetup') {
      return (
        <ISSetup
          setCurrentPage={setCurrentPage}
          personas={personas}
        />
      );
    } else {
      return null;
    }
  };

  return (
    <DndProvider backend={HTML5Backend}>
      <div className="App">
        <Navbar setCurrentPage={setCurrentPage} />
        {renderPage()}
      </div>
    </DndProvider>
  );
}

export default App;
