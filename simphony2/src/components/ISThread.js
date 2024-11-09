// src/components/ISThread.js
import React, { useState, useEffect } from 'react';
import './ISThread.css';
import { useAuth } from './AuthProvider';
import { firestore } from '../firebase';
import { FaCog, FaSave } from 'react-icons/fa';
import { useNavigate } from 'react-router-dom';

function ISThread() {
  const { currentUser } = useAuth();
  const navigate = useNavigate();
  // Removed: const history = useHistory(true);
  const [threadOutputs, setThreadOutputs] = useState([]);
  const [isPaused, setIsPaused] = useState(false);
  const [conductorModel, setConductorModel] = useState('phi3:14b-medium-128k-instruct-fp16');
  const [loading, setLoading] = useState(true);
  const [conductorOutputs, setConductorOutputs] = useState([]);

  // Simulate fetching thread data (replace with actual implementation)
  useEffect(() => {
    // Fetch thread data from Firestore or other sources
    // For demonstration, we'll use dummy data
    const dummyThread = [
      { persona: 'Persona 1', output: 'Output from Persona 1' },
      { persona: 'Persona 2', output: 'Output from Persona 2' },
      // Add more as needed
    ];

    setThreadOutputs(dummyThread);
    setLoading(false);
  }, []);

  const handlePause = () => {
    setIsPaused(!isPaused);
  };

  const handleSaveThread = () => {
    // Save threadOutputs and conductorOutputs to Firestore
    const threadData = {
      userId: currentUser.uid,
      threadOutputs,
      conductorOutputs,
      conductorModel,
      timestamp: new Date(),
    };

    firestore.collection('isThreads').add(threadData)
      .then(() => {
        alert('IS:Thread saved successfully!');
        navigate('/my-arrays'); // Redirect or handle as needed
      })
      .catch((error) => {
        console.error("Error saving IS:Thread: ", error);
        alert('Failed to save IS:Thread.');
      });
  };

  const handleModelChange = (e) => {
    setConductorModel(e.target.value);
  };

  const handleConductorSelection = () => {
    // Logic to change conductor model
    // For demonstration, it's already handled via handleModelChange
  };

  return (
    <div className="is-thread-container">
      <div className="is-thread-header">
        <div className="header-left">
          <button className="pause-button" onClick={handlePause}>
            {isPaused ? 'RESUME SEQUENCE' : 'PAUSE SEQUENCE'}
          </button>
          <button className="save-thread-button" onClick={handleSaveThread}>
            SAVE IS:THREAD <FaSave />
          </button>
        </div>
        <h2 className="page-title">IS:Thread</h2>
        <div className="header-right">
          <FaCog size={24} className="settings-icon" />
        </div>
      </div>

      <div className="conductor-selector">
        <label>S&P-Conductor:</label>
        <select value={conductorModel} onChange={handleModelChange}>
          <option value="phi3:14b-medium-128k-instruct-fp16">phi3:14b-medium-128k-instruct-fp16</option>
          <option value="phi3:medium-128k">phi3:medium-128k</option>
          <option value="mistral-demo">mistral-demo</option>
        </select>
      </div>

      <div className="thread-content">
        <div className="left-section">
          <img src="/simphony-logo.gif" alt="Simphony Logo" className="simphony-logo" />
          <div className="conductor-output">
            {conductorOutputs.map((output, index) => (
              <div key={index} className="conductor-entry">
                <span className="toggle-button">▶</span>
                <div className="conductor-text">{output}</div>
              </div>
            ))}
          </div>
        </div>
        <div className="right-section">
          {threadOutputs.map((output, index) => (
            <div key={index} className="output-entry">
              <div className="persona-header">{output.persona}</div>
              <div className="output-text">{output.output}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default ISThread;
