// src/components/HeaderButtons.js
import React from 'react';
import { FaCog } from 'react-icons/fa';
import './HeaderButtons.css';

function HeaderButtons({
  mainButtonLabel,
  mainButtonColor,
  secondaryButtonLabel,
  onSecondaryButtonClick, // Updated prop name
  setCurrentPage,
  nextPage, // Optional, can be used if needed
  pageTitle,
}) {
  return (
    <div className="header-buttons">
      <div className="header-left">
        <button
          className="main-button"
          style={{ backgroundColor: mainButtonColor }}
          onClick={setCurrentPage}
        >
          {mainButtonLabel}
        </button>
        {secondaryButtonLabel && onSecondaryButtonClick && (
          <button className="secondary-button" onClick={onSecondaryButtonClick}>
            {secondaryButtonLabel}
          </button>
        )}
      </div>
      <h2 className="page-title">{pageTitle}</h2>
      <div className="header-right">
        <FaCog size={24} className="settings-icon" />
      </div>
    </div>
  );
}

export default HeaderButtons;
