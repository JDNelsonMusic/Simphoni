// src/components/MyArrays.js
import React, { useEffect, useState } from 'react';
import { firestore } from '../firebase';
import { useAuth } from './AuthProvider';
import './MyArrays.css';

function MyArrays() {
  const { currentUser } = useAuth();
  const [personalArrays, setPersonalArrays] = useState([]);
  const [sharedArrays, setSharedArrays] = useState([]);
  const [publicArrays, setPublicArrays] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const unsubscribe = firestore.collection('arrays').onSnapshot(snapshot => {
      const personal = [];
      const shared = [];
      const publicA = [];

      snapshot.forEach(doc => {
        const data = doc.data();
        if (data.owner === currentUser.uid) {
          personal.push({ id: doc.id, ...data });
        } else if (data.access === 'Exclusive' && data.allowedUsers.includes(currentUser.uid)) {
          shared.push({ id: doc.id, ...data });
        } else if (data.access === 'Public') {
          publicA.push({ id: doc.id, ...data });
        }
      });

      setPersonalArrays(personal);
      setSharedArrays(shared);
      setPublicArrays(publicA);
      setLoading(false);
    });

    return unsubscribe;
  }, [currentUser]);

  if (loading) {
    return <div className="loading">Loading Arrays...</div>;
  }

  return (
    <div className="my-arrays-container">
      <h2>My Arrays</h2>

      <div className="arrays-section">
        <h3>Personal Arrays</h3>
        {personalArrays.length > 0 ? (
          <ul>
            {personalArrays.map(array => (
              <li key={array.id}>
                <strong>{array.name}</strong> - {array.access}
                {/* Add buttons or links for actions like Edit, Delete, Load */}
              </li>
            ))}
          </ul>
        ) : (
          <p>No Personal Arrays found.</p>
        )}
      </div>

      <div className="arrays-section">
        <h3>Shared Arrays</h3>
        {sharedArrays.length > 0 ? (
          <ul>
            {sharedArrays.map(array => (
              <li key={array.id}>
                <strong>{array.name}</strong> - {array.access}
                {/* Add buttons or links for actions like View, Load */}
              </li>
            ))}
          </ul>
        ) : (
          <p>No Shared Arrays found.</p>
        )}
      </div>

      <div className="arrays-section">
        <h3>Public Arrays</h3>
        {publicArrays.length > 0 ? (
          <ul>
            {publicArrays.map(array => (
              <li key={array.id}>
                <strong>{array.name}</strong> - {array.access}
                {/* Add buttons or links for actions like View, Load */}
              </li>
            ))}
          </ul>
        ) : (
          <p>No Public Arrays found.</p>
        )}
      </div>
    </div>
  );
}

export default MyArrays;
