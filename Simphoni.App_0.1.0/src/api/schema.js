// src/api/schema.js
import { functions } from '../firebase';
import { httpsCallable } from 'firebase/functions';

// Load Schema
export const fetchLoadSchema = async () => {
  const loadSchema = httpsCallable(functions, 'loadSchema');
  try {
    const result = await loadSchema();
    return result.data.schema;
  } catch (error) {
    console.error("Load Schema Error:", error);
    throw error;
  }
};

// Save Schema
export const fetchSaveSchema = async (schema) => {
  const saveSchema = httpsCallable(functions, 'saveSchema');
  try {
    const result = await saveSchema({ schema });
    return result.data.success;
  } catch (error) {
    console.error("Save Schema Error:", error);
    throw error;
  }
};
