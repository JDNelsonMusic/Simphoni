// src/components/InstructSequenceSetup.js
import React, { useState, useEffect } from 'react';
import { DragDropContext, Droppable, Draggable } from 'react-beautiful-dnd';

// Sample AI Models - In a real application, these would be fetched from the backend or Ollama
const availableModels = [
  { id: 'model-1', name: 'mistral-nemo' },
  { id: 'model-2', name: 'smol-m13b' },
  { id: 'model-3', name: 'orca-mini-70b' },
  { id: 'model-4', name: 'stable-diffusion' },
  { id: 'model-5', name: 'llama3.2t' },
  // Add more models as needed
];

const InstructSequenceSetup = () => {
  const [instructionFields, setInstructionFields] = useState([]);
  const [availableModelsList, setAvailableModelsList] = useState(availableModels);

  useEffect(() => {
    // Load saved instruct sequences from localStorage on component mount
    const savedSequences = JSON.parse(localStorage.getItem('instructSequences')) || [];
    setInstructionFields(savedSequences);
  }, []);

  const handleAddInstruction = () => {
    if (instructionFields.length >= 16) {
      alert('You can only add up to sixteen instruction fields.');
      return;
    }
    const newField = {
      id: `instruction-${Date.now()}`,
      model: null,
      parameters: {},
    };
    setInstructionFields([...instructionFields, newField]);
  };

  const handleRemoveInstruction = (id) => {
    const updatedFields = instructionFields.filter((field) => field.id !== id);
    setInstructionFields(updatedFields);
    localStorage.setItem('instructSequences', JSON.stringify(updatedFields));
  };

  const handleDragEnd = (result) => {
    const { source, destination, draggableId } = result;

    if (!destination) return;

    // If dragging from available models to instruction fields
    if (source.droppableId === 'availableModels' && destination.droppableId.startsWith('instruction-')) {
      const fieldId = destination.droppableId;
      const fieldIndex = instructionFields.findIndex((field) => field.id === fieldId);
      const selectedModel = availableModels.find((model) => model.id === draggableId);

      const updatedFields = [...instructionFields];
      updatedFields[fieldIndex].model = selectedModel;

      setInstructionFields(updatedFields);
      localStorage.setItem('instructSequences', JSON.stringify(updatedFields));
      return;
    }

    // If reordering within instruction fields or other logic can be added here
  };

  const handleSaveSequence = () => {
    localStorage.setItem('instructSequences', JSON.stringify(instructionFields));
    alert('Instruct sequence saved successfully!');
  };

  const handleLoadSequence = () => {
    const savedSequences = JSON.parse(localStorage.getItem('instructSequences')) || [];
    setInstructionFields(savedSequences);
    alert('Instruct sequence loaded successfully!');
  };

  return (
    <div className="p-6 bg-gray-800 text-white">
      <h2 className="text-2xl mb-4">Instruct Sequence Setup</h2>
      <div className="mb-6">
        <button
          onClick={handleAddInstruction}
          className="bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded"
        >
          Add Instruction Field
        </button>
        <button
          onClick={handleSaveSequence}
          className="bg-green-600 hover:bg-green-700 text-white py-2 px-4 rounded ml-4"
        >
          Save Sequence
        </button>
        <button
          onClick={handleLoadSequence}
          className="bg-yellow-600 hover:bg-yellow-700 text-white py-2 px-4 rounded ml-4"
        >
          Load Sequence
        </button>
      </div>
      <DragDropContext onDragEnd={handleDragEnd}>
        <div className="flex space-x-6">
          {/* Available Models List */}
          <Droppable droppableId="availableModels">
            {(provided) => (
              <div
                className="w-1/4 p-4 bg-gray-700 rounded"
                ref={provided.innerRef}
                {...provided.droppableProps}
              >
                <h3 className="text-xl mb-2">Available Models</h3>
                {availableModelsList.map((model, index) => (
                  <Draggable key={model.id} draggableId={model.id} index={index}>
                    {(provided) => (
                      <div
                        className="bg-gray-600 p-2 mb-2 rounded cursor-pointer"
                        ref={provided.innerRef}
                        {...provided.draggableProps}
                        {...provided.dragHandleProps}
                      >
                        {model.name}
                      </div>
                    )}
                  </Draggable>
                ))}
                {provided.placeholder}
              </div>
            )}
          </Droppable>

          {/* Instruction Fields */}
          <div className="w-3/4">
            {instructionFields.map((field, index) => (
              <Droppable droppableId={field.id} key={field.id}>
                {(provided) => (
                  <div
                    className="mb-4 p-4 bg-gray-700 rounded"
                    ref={provided.innerRef}
                    {...provided.droppableProps}
                  >
                    <div className="flex justify-between items-center mb-2">
                      <h4 className="text-lg">Instruction Field {index + 1}</h4>
                      <button
                        onClick={() => handleRemoveInstruction(field.id)}
                        className="bg-red-500 hover:bg-red-600 text-white py-1 px-3 rounded"
                      >
                        Delete
                      </button>
                    </div>
                    <Droppable droppableId={field.id}>
                      {(provided, snapshot) => (
                        <div
                          className={`p-2 rounded ${snapshot.isDraggingOver ? 'bg-blue-400' : 'bg-gray-600'}`}
                          ref={provided.innerRef}
                          {...provided.droppableProps}
                        >
                          {field.model ? (
                            <div className="flex justify-between items-center">
                              <span>{field.model.name}</span>
                              <button
                                onClick={() => {
                                  const updatedFields = instructionFields.map((f) =>
                                    f.id === field.id ? { ...f, model: null } : f
                                  );
                                  setInstructionFields(updatedFields);
                                  localStorage.setItem('instructSequences', JSON.stringify(updatedFields));
                                }}
                                className="bg-red-500 hover:bg-red-600 text-white py-1 px-2 rounded"
                              >
                                Remove
                              </button>
                            </div>
                          ) : (
                            <div className="text-center text-gray-300">
                              Drag a model here to assign
                            </div>
                          )}
                          {provided.placeholder}
                        </div>
                      )}
                    </Droppable>
                    {/* Additional Parameters Configuration */}
                    {field.model && (
                      <div className="mt-4">
                        <label className="block mb-2">Parameters for {field.model.name}:</label>
                        {/* Example parameter input - can be expanded based on model requirements */}
                        <input
                          type="text"
                          name={`param-${field.id}`}
                          placeholder="Enter parameter value"
                          className="w-full p-2 rounded bg-gray-600 text-white"
                          // Handle parameter changes as needed
                        />
                      </div>
                    )}
                  </div>
                )}
              </Droppable>
            ))}
          </div>
        </div>
      </DragDropContext>
      {/* Optional: Display Current Sequence */}
      <div className="mt-8">
        <h3 className="text-xl mb-4">Current Instruct Sequence</h3>
        {instructionFields.length === 0 ? (
          <p>No instruct sequences defined.</p>
        ) : (
          <ol className="list-decimal list-inside">
            {instructionFields.map((field, index) => (
              <li key={field.id} className="mb-2">
                {field.model ? field.model.name : 'Unassigned Model'}
              </li>
            ))}
          </ol>
        )}
      </div>
    </div>
  );
};

export default InstructSequenceSetup;
