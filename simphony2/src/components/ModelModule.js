// src/components/ModelModule.js
import React from 'react';
import { useDrag } from 'react-dnd';
import './ModelModule.css';

function ModelModule({ model }) {
  const [{ isDragging }, drag] = useDrag(() => ({
    type: 'model',
    item: { model },
    collect: (monitor) => ({
      isDragging: !!monitor.isDragging(),
    }),
  }), [model]);

  return (
    <div
      className="model-module"
      ref={drag}
      style={{ opacity: isDragging ? 0.5 : 1 }}
    >
      {model.display}
    </div>
  );
}

export default ModelModule;
