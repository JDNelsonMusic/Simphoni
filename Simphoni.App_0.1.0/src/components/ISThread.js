// src/components/ISThread.js
import React, { useState } from 'react';
import './ISThread.css';

function ISThread() {
  const [selectedModel, setSelectedModel] = useState('');
  const [prompt, setPrompt] = useState('');
  const [response, setResponse] = useState('');
  const [image, setImage] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const models = [
    // ChatGPT models
    { label: 'KEE1:txt (ChatGPT)', value: 'gpt-4o-txt' },
    { label: 'KEE1:web (ChatGPT)', value: 'gpt-4o-web' },
    { label: 'KEE1:img (ChatGPT)', value: 'gpt-4o-img' },
    { label: 'KEE1:vid (ChatGPT)', value: 'gpt-4o-vid' },
    { label: 'KEE1:code (ChatGPT)', value: 'gpt-4o-code' },
    // Ollama models (replace with actual model names)
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
    { name: 'smolm2:1.7b', display: 'smolm2:1.7b' }
    // Stable Diffusion
    // { label: 'Stable Diffusion:3.5b', value: 'stable-diffusion:3.5b' },
  ];

  const handleModelChange = (e) => {
    setSelectedModel(e.target.value);
    setResponse('');
    setImage(null);
  };

  const handlePromptChange = (e) => {
    setPrompt(e.target.value);
  };

  const handleSubmit = async () => {
    if (!selectedModel) {
      alert('Please select a model.');
      return;
    }
    if (!prompt.trim()) {
      alert('Please enter a prompt.');
      return;
    }

    setIsLoading(true);
    setResponse('');
    setImage(null);

    try {
      if (selectedModel.startsWith('gpt-4o')) {
        // ChatGPT models
        const res = await fetch('http://localhost:8000/chat', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ prompt }),
        });
        const data = await res.json();
        if (res.ok) {
          setResponse(data.reply);
        } else {
          setResponse(`Error: ${data.detail}`);
        }
      } else if (selectedModel.startsWith('ollama-')) {
        // Ollama models
        const res = await fetch('http://localhost:8000/ollama', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ model: selectedModel, prompt }),
        });
        const data = await res.json();
        if (res.ok) {
          setResponse(data.reply);
        } else {
          setResponse(`Error: ${data.detail}`);
        }
      } else if (selectedModel === 'stable-diffusion:3.5b') {
        // Stable Diffusion
        const res = await fetch('http://localhost:8000/stable-diffusion', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ prompt }),
        });
        const data = await res.json();
        if (res.ok) {
          setImage(`data:image/png;base64,${data.image}`);
        } else {
          setResponse(`Error: ${data.detail}`);
        }
      } else {
        setResponse('Unknown model selected.');
      }
    } catch (error) {
      console.error('Error:', error);
      setResponse('An error occurred while processing your request.');
    }

    setIsLoading(false);
  };

  return (
    <div className="is-thread-container">
      <h2>IS:Thread Page</h2>
      <div className="model-selector">
        <label htmlFor="model-select">Select Model:</label>
        <select id="model-select" value={selectedModel} onChange={handleModelChange}>
          <option value="">-- Select a Model --</option>
          {models.map((model, index) => (
            <option key={index} value={model.value}>
              {model.label}
            </option>
          ))}
        </select>
      </div>
      <div className="prompt-input">
        <label htmlFor="prompt">Enter Prompt:</label>
        <textarea
          id="prompt"
          value={prompt}
          onChange={handlePromptChange}
          placeholder="Type your prompt here..."
        />
      </div>
      <button onClick={handleSubmit} disabled={isLoading}>
        {isLoading ? 'Processing...' : 'Send'}
      </button>
      <div className="response-section">
        {response && (
          <div className="text-response">
            <h3>Response:</h3>
            <p>{response}</p>
          </div>
        )}
        {image && (
          <div className="image-response">
            <h3>Generated Image:</h3>
            <img src={image} alt="Generated" />
          </div>
        )}
      </div>
    </div>
  );
}

export default ISThread;
