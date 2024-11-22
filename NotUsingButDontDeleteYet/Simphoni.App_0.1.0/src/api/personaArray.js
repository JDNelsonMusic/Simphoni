// src/api/personaArray.js
import { functions } from '../firebase';
import { httpsCallable } from 'firebase/functions';

// Load Persona Array
export const fetchLoadPersonaArray = async () => {
  const loadPersonaArray = httpsCallable(functions, 'loadPersonaArray');
  try {
    const result = await loadPersonaArray();
    return result.data.personaArray;
  } catch (error) {
    console.error("Load Persona Array Error:", error);
    throw error;
  }
};

// Save Persona Array
export const fetchSavePersonaArray = async (personaArray) => {
  const savePersonaArray = httpsCallable(functions, 'savePersonaArray');
  try {
    const result = await savePersonaArray({ personaArray });
    return result.data.success;
  } catch (error) {
    console.error("Save Persona Array Error:", error);
    throw error;
  }
};
