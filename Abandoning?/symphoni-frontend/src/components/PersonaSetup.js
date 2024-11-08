// src/components/PersonaSetup.js
import React, { useState, useEffect } from 'react';

const PersonaSetup = () => {
  const [personas, setPersonas] = useState([]);
  const [currentPersona, setCurrentPersona] = useState({
    nickname: '',
    adherence: 5,
    creativity: 5,
    image: null,
    imagePreview: null,
  });

  useEffect(() => {
    // Load saved personas from localStorage on component mount
    const savedPersonas = JSON.parse(localStorage.getItem('personas')) || [];
    setPersonas(savedPersonas);
  }, []);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setCurrentPersona({ ...currentPersona, [name]: value });
  };

  const handleSliderChange = (e) => {
    const { name, value } = e.target;
    setCurrentPersona({ ...currentPersona, [name]: Number(value) });
  };

  const handleImageUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      setCurrentPersona({
        ...currentPersona,
        image: file,
        imagePreview: URL.createObjectURL(file),
      });
    }
  };

  const handleSavePersona = () => {
    if (!currentPersona.nickname) {
      alert('Please enter a nickname for the persona.');
      return;
    }
    const newPersona = { ...currentPersona };
    setPersonas([...personas, newPersona]);
    localStorage.setItem('personas', JSON.stringify([...personas, newPersona]));
    setCurrentPersona({
      nickname: '',
      adherence: 5,
      creativity: 5,
      image: null,
      imagePreview: null,
    });
  };

  const handleLoadPersona = (persona) => {
    setCurrentPersona(persona);
  };

  const handleDeletePersona = (index) => {
    const updatedPersonas = personas.filter((_, i) => i !== index);
    setPersonas(updatedPersonas);
    localStorage.setItem('personas', JSON.stringify(updatedPersonas));
  };

  return (
    <div className="p-6 bg-gray-800 text-white">
      <h2 className="text-2xl mb-4">Persona Setup</h2>
      <div className="mb-6">
        <label className="block mb-2">Nickname:</label>
        <input
          type="text"
          name="nickname"
          value={currentPersona.nickname}
          onChange={handleChange}
          className="w-full p-2 rounded bg-gray-700"
          placeholder="Enter persona nickname"
        />
      </div>
      <div className="mb-6">
        <label className="block mb-2">Prompt Adherence: {currentPersona.adherence}</label>
        <input
          type="range"
          name="adherence"
          min="1"
          max="10"
          value={currentPersona.adherence}
          onChange={handleSliderChange}
          className="w-full"
        />
      </div>
      <div className="mb-6">
        <label className="block mb-2">Creativity: {currentPersona.creativity}</label>
        <input
          type="range"
          name="creativity"
          min="1"
          max="10"
          value={currentPersona.creativity}
          onChange={handleSliderChange}
          className="w-full"
        />
      </div>
      <div className="mb-6">
        <label className="block mb-2">Upload Image:</label>
        <input
          type="file"
          accept="image/*"
          onChange={handleImageUpload}
          className="w-full"
        />
        {currentPersona.imagePreview && (
          <img
            src={currentPersona.imagePreview}
            alt="Persona Preview"
            className="mt-4 w-32 h-32 object-cover rounded-full"
          />
        )}
      </div>
      <button
        onClick={handleSavePersona}
        className="bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded"
      >
        Save Persona
      </button>

      <div className="mt-8">
        <h3 className="text-xl mb-4">Saved Personas</h3>
        {personas.length === 0 ? (
          <p>No personas saved.</p>
        ) : (
          <ul>
            {personas.map((persona, index) => (
              <li key={index} className="flex items-center justify-between bg-gray-700 p-4 mb-2 rounded">
                <div className="flex items-center">
                  {persona.imagePreview && (
                    <img
                      src={persona.imagePreview}
                      alt={`${persona.nickname} Image`}
                      className="w-12 h-12 object-cover rounded-full mr-4"
                    />
                  )}
                  <div>
                    <p className="font-bold">{persona.nickname}</p>
                    <p>Adherence: {persona.adherence}</p>
                    <p>Creativity: {persona.creativity}</p>
                  </div>
                </div>
                <div className="flex space-x-2">
                  <button
                    onClick={() => handleLoadPersona(persona)}
                    className="bg-green-500 hover:bg-green-600 text-white py-1 px-3 rounded"
                  >
                    Load
                  </button>
                  <button
                    onClick={() => handleDeletePersona(index)}
                    className="bg-red-500 hover:bg-red-600 text-white py-1 px-3 rounded"
                  >
                    Delete
                  </button>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
};

export default PersonaSetup;
