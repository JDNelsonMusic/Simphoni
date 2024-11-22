// src/context/AppContext.js
import React, { createContext, useState } from 'react';

export const AppContext = createContext();

export const AppProvider = ({ children }) => {
  const [personas, setPersonas] = useState(
    Array.from({ length: 9 }, () => ({
      id: `${Date.now()}_${Math.random()}`, // Unique ID
      nickname: '',
      model: 'llama3.2:3b',
      creativity: 5,
      definePersona: '',
    }))
  );

  const [schemas, setSchemas] = useState([]);
  const [loops, setLoops] = useState([]);
  const [arrayName, setArrayName] = useState(''); // Added arrayName state

  return (
    <AppContext.Provider
      value={{
        personas,
        setPersonas,
        schemas,
        setSchemas,
        loops,
        setLoops,
        arrayName,
        setArrayName, // Provided setArrayName in context
      }}
    >
      {children}
    </AppContext.Provider>
  );
};
