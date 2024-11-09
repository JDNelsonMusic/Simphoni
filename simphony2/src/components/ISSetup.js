// src/components/ISSetup.js
import React, { useState, useEffect } from 'react';
import HeaderButtons from './HeaderButtons';
import ActivePersonas from './ActivePersonas';
import InstructLine from './InstructLine';
import { firestore } from '../firebase';
import { useAuth } from './AuthProvider';
import { useNavigate } from 'react-router-dom';
import './ISSetup.css';

function ISSetup() {
  const { currentUser } = useAuth();
  const navigate = useNavigate();
  const [instructLines, setInstructLines] = useState([]);
  const [loading, setLoading] = useState(true);

  // Fetch user's persona arrays for assigning
  const [personaArray, setPersonaArray] = useState([]);

  useEffect(() => {
    const fetchPersonaArray = async () => {
      try {
        const querySnapshot = await firestore.collection('personaArrays')
          .where('owner', '==', currentUser.uid)
          .get();

        if (querySnapshot.empty) {
          alert('No Persona Array found. Please set up your personas first.');
          navigate('/persona-setup'); // Redirect to PersonaSetup
          return;
        }

        const doc = querySnapshot.docs[0];
        const data = doc.data();

        setPersonaArray(data.personas || []);
        setLoading(false);
      } catch (error) {
        console.error('Error fetching personaArray:', error);
        setLoading(false);
      }
    };

    fetchPersonaArray();
  }, [currentUser, navigate]);

  useEffect(() => {
    // Initialize instructLines with nine instruct lines
    const initialInstructLines = Array.from({ length: 9 }, (_, index) => ({
      id: index,
      instructText: '',
      persona: null,
      tool: '',
      file: null,
    }));
    setInstructLines(initialInstructLines);
  }, []);

  const handleNumLinesChange = (e) => {
    const newNum = parseInt(e.target.value, 10) || 0;
    const updatedInstructLines = Array.from({ length: newNum }, (_, index) => ({
      id: index,
      instructText: '',
      persona: null,
      tool: '',
      file: null,
    }));
    setInstructLines(updatedInstructLines);
  };

  const updateInstructLine = (index, data) => {
    const newInstructLines = [...instructLines];
    newInstructLines[index] = { ...newInstructLines[index], ...data };
    setInstructLines(newInstructLines);
  };

  const saveInstructSequence = async () => {
    const sequenceName = prompt("Enter a name for this Instruct Sequence:");
    if (!sequenceName) {
      alert("Sequence name is required.");
      return;
    }

    const accessLevel = prompt("Enter access level (Private, Exclusive, Public):", "Private");
    if (!['Private', 'Exclusive', 'Public'].includes(accessLevel)) {
      alert("Invalid access level.");
      return;
    }

    let allowedUsers = [];
    if (accessLevel === 'Exclusive') {
      const usersInput = prompt("Enter user emails separated by commas:");
      if (usersInput) {
        const emails = usersInput.split(',').map(email => email.trim());
        // Fetch user IDs based on emails
        const userRefs = await Promise.all(emails.map(email =>
          firestore.collection('users').where('email', '==', email).get()
        ));
        userRefs.forEach(querySnapshot => {
          querySnapshot.forEach(doc => {
            allowedUsers.push(doc.id);
          });
        });
      }
    }

    const newSequence = {
      name: sequenceName,
      owner: currentUser.uid,
      access: accessLevel,
      allowedUsers,
      instructLines,
      timestamp: new Date()
    };

    try {
      await firestore.collection('instructSequences').add(newSequence);
      alert("Instruct Sequence saved successfully!");
    } catch (error) {
      console.error("Error saving Instruct Sequence: ", error);
      alert("Failed to save Instruct Sequence.");
    }
  };

  const startSequence = () => {
    // Navigate to '/is-thread'
    navigate('/is-thread');
  };

  if (loading) {
    return <div className="loading">Loading IS:Setup...</div>;
  }

  return (
    <div className="is-setup">
      <HeaderButtons
        mainButtonLabel="START SEQUENCE"
        mainButtonColor="#FF007C"
        secondaryButtonLabel="SAVE NEW INSTRUCT SEQUENCE"
        savePersonaArray={saveInstructSequence}
        setCurrentPage={startSequence} // Navigates to '/is-thread'
        nextPage="/is-thread" // Optional, can be removed if not used
        pageTitle="Instruct Sequence Setup"
      />
      <div className="num-lines-input">
        <label>Number of Instruct Lines:</label>
        <input
          type="number"
          value={instructLines.length}
          onChange={handleNumLinesChange}
          min="1"
          max="20" // Set a reasonable max limit
        />
      </div>
      <ActivePersonas personas={personaArray} />
      <div className="instruct-lines">
        {instructLines.map((line, index) => (
          <InstructLine
            key={line.id}
            index={index}
            data={line}
            updateInstructLine={updateInstructLine}
          />
        ))}
      </div>
    </div>
  );
}

export default ISSetup;
