import React from 'react';
import './HeaderButtons.css';

function HeaderButtons({ savePersonaArray }) {
  return (
    <div className="header-buttons">
      <button className="continue-btn">CONTINUE TO INSTRUCT SETUP</button>
      <button className="save-array-btn" onClick={savePersonaArray}>SAVE PERSONA ARRAY</button>
      <span className="settings-icon">⚙️</span>
    </div>
  );
}

export default HeaderButtons;
