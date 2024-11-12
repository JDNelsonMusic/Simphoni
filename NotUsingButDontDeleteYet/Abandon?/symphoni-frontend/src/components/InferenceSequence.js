// src/components/InferenceSequence.js
import React, { useState, useEffect } from 'react';
import ReactFlow, { ReactFlowProvider } from 'react-flow-renderer';
// Optional: Import visualization library if needed
// import ReactFlow from 'react-flow-renderer';

const InferenceSequence = () => {
  const [inferenceSteps, setInferenceSteps] = useState([]);
  const [summarization, setSummarization] = useState('');
  const [currentPrompt, setCurrentPrompt] = useState('');
  const [executionMode, setExecutionMode] = useState('sequential'); // 'sequential' or 'parallel'

  useEffect(() => {
    // Load saved inference sequences from localStorage on component mount
    const savedSteps = JSON.parse(localStorage.getItem('inferenceSteps')) || [];
    const savedSummarization = localStorage.getItem('inferenceSummarization') || '';
    setInferenceSteps(savedSteps);
    setSummarization(savedSummarization);
  }, []);

  const handleAddStep = () => {
    const newStep = {
      id: `step-${Date.now()}`,
      prompt: '',
      output: '',
      model: '',
      editable: true,
    };
    setInferenceSteps([...inferenceSteps, newStep]);
  };

  const handleRemoveStep = (id) => {
    const updatedSteps = inferenceSteps.filter((step) => step.id !== id);
    setInferenceSteps(updatedSteps);
    localStorage.setItem('inferenceSteps', JSON.stringify(updatedSteps));
  };

  const handlePromptChange = (id, value) => {
    const updatedSteps = inferenceSteps.map((step) =>
      step.id === id ? { ...step, prompt: value } : step
    );
    setInferenceSteps(updatedSteps);
  };

  const handleOutputChange = (id, value) => {
    const updatedSteps = inferenceSteps.map((step) =>
      step.id === id ? { ...step, output: value } : step
    );
    setInferenceSteps(updatedSteps);
  };

  const handleModelChange = (id, value) => {
    const updatedSteps = inferenceSteps.map((step) =>
      step.id === id ? { ...step, model: value } : step
    );
    setInferenceSteps(updatedSteps);
  };

  const handleSummarizationChange = (value) => {
    setSummarization(value);
  };

  const handleExecutionModeChange = (e) => {
    setExecutionMode(e.target.value);
  };

  const handleSaveSequence = () => {
    localStorage.setItem('inferenceSteps', JSON.stringify(inferenceSteps));
    localStorage.setItem('inferenceSummarization', summarization);
    alert('Inference sequence saved successfully!');
  };

  const handleLoadSequence = () => {
    const savedSteps = JSON.parse(localStorage.getItem('inferenceSteps')) || [];
    const savedSummarization = localStorage.getItem('inferenceSummarization') || '';
    setInferenceSteps(savedSteps);
    setSummarization(savedSummarization);
    alert('Inference sequence loaded successfully!');
  };

    // Prepare elements for ReactFlow
    const elements = inferenceSteps.map((step, index) => ({
        id: step.id,
        type: 'default',
        data: { label: `${index + 1}. ${step.model || 'Unassigned Model'}` },
        position: { x: 100 * index, y: 100 },
      })).flatMap((node, index, arr) => {
        if (index === 0) return [node];
        const edge = {
          id: `e${arr[index - 1].id}-${node.id}`,
          source: arr[index - 1].id,
          target: node.id,
          animated: true,
        };
        return [node, edge];
      });

      return (
        <div className="p-6 bg-gray-800 text-white">
          {/* ... existing JSX */}
          
          {/* Optional: Visualization of Data Flow */}
          <div className="mb-6">
            <h3 className="text-xl mb-4">Data Flow Visualization</h3>
            {inferenceSteps.length === 0 ? (
              <p>No inference steps to visualize.</p>
            ) : (
              <div className="h-96 border border-gray-600 rounded">
                <ReactFlowProvider>
                  <ReactFlow elements={elements} />
                </ReactFlowProvider>
              </div>
            )}
          </div>
        </div>
      );
    };

    export default InferenceSequence;

