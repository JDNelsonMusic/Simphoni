// src/api/otherApis.js
import { functions } from '../firebase';
import { httpsCallable } from 'firebase/functions';

// Fetch ChatGPT Response
export const fetchChatGptResponse = async (prompt) => {
  const getChatGptResponse = httpsCallable(functions, 'getChatGptResponse');
  try {
    const result = await getChatGptResponse({ prompt });
    return result.data;
  } catch (error) {
    console.error("Error fetching ChatGPT response:", error);
    throw error;
  }
};

// Fetch Ollama Response
export const fetchOllamaResponse = async (prompt, model) => {
  const getOllamaResponse = httpsCallable(functions, 'getOllamaResponse');
  try {
    const result = await getOllamaResponse({ prompt, model });
    return result.data;
  } catch (error) {
    console.error("Error fetching Ollama response:", error);
    throw error;
  }
};

// Fetch Generated Image
export const fetchGeneratedImage = async (prompt) => {
  const getGeneratedImage = httpsCallable(functions, 'getGeneratedImage');
  try {
    const result = await getGeneratedImage({ prompt });
    return result.data;
  } catch (error) {
    console.error("Error fetching generated image:", error);
    throw error;
  }
};
