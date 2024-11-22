// src/components/Settings.js
import React, { useState } from 'react';
import './Settings.css'; // Optional: If you want separate styles

const Settings = ({ onClose }) => {
  const [theme, setTheme] = useState('dark');
  const [textSize, setTextSize] = useState('medium');

  const handleSave = () => {
    // Save settings to localStorage or backend
    localStorage.setItem('theme', theme);
    localStorage.setItem('textSize', textSize);
    alert("Settings saved!");
    onClose();
    // Optionally, implement context or global state updates
  };

  return (
    <div className="settings-modal">
      <div className="settings-content">
        <h3>Settings</h3>
        <label>
          Theme:
          <select value={theme} onChange={(e) => setTheme(e.target.value)}>
            <option value="dark">Dark</option>
            <option value="light">Light</option>
          </select>
        </label>
        <label>
          Text Size:
          <select value={textSize} onChange={(e) => setTextSize(e.target.value)}>
            <option value="small">Small</option>
            <option value="medium">Medium</option>
            <option value="large">Large</option>
          </select>
        </label>
        <button onClick={handleSave}>Save</button>
        <button className="close-btn" onClick={onClose}>Close</button>
      </div>
    </div>
  );
};

export default Settings;
