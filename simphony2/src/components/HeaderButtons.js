// src/components/HeaderButtons.js
import React from 'react';
import './HeaderButtons.css';
import { FaCog } from 'react-icons/fa';

function HeaderButtons({
  mainButtonLabel,
  mainButtonColor,
  secondaryButtonLabel,
  savePersonaArray,
  setCurrentPage,
  nextPage,
  pageTitle, // Prop to handle different titles
}) {
  const handleMainButtonClick = () => {
    if (setCurrentPage && typeof setCurrentPage === 'function') {
      setCurrentPage(nextPage);
    } else {
      console.error("setCurrentPage is not a function or is undefined");
    }
  };

  return (
    <div className="header-buttons">
      <div className="header-left">
        <button
          className="main-button"
          onClick={handleMainButtonClick}
          style={{ color: mainButtonColor, borderColor: mainButtonColor }}
        >
          {mainButtonLabel}
        </button>
        {secondaryButtonLabel && (
          <button
            className="secondary-button"
            onClick={savePersonaArray}
          >
            {secondaryButtonLabel}
          </button>
        )}
      </div>
      <h2 className="page-title">{pageTitle}</h2>
      <div className="header-right">
        <FaCog size={24} className="settings-icon" onClick={() => alert('Open Settings')} />
      </div>
    </div>
  );
}

export default HeaderButtons;
