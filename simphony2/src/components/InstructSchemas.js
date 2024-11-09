// src/components/InstructSchemas.js
import React, { useEffect, useState } from 'react';
import { firestore } from '../firebase';
import { useAuth } from './AuthProvider';
import './InstructSchemas.css';

function InstructSchemas() {
  const { currentUser } = useAuth();
  const [privateSchemas, setPrivateSchemas] = useState([]);
  const [sharedSchemas, setSharedSchemas] = useState([]);
  const [publicSchemas, setPublicSchemas] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const unsubscribe = firestore.collection('instructSchemas').onSnapshot(snapshot => {
      const privateS = [];
      const sharedS = [];
      const publicS = [];

      snapshot.forEach(doc => {
        const data = doc.data();
        if (data.owner === currentUser.uid) {
          privateS.push({ id: doc.id, ...data });
        } else if (data.access === 'Exclusive' && data.allowedUsers.includes(currentUser.uid)) {
          sharedS.push({ id: doc.id, ...data });
        } else if (data.access === 'Public') {
          publicS.push({ id: doc.id, ...data });
        }
      });

      setPrivateSchemas(privateS);
      setSharedSchemas(sharedS);
      setPublicSchemas(publicS);
      setLoading(false);
    });

    return unsubscribe;
  }, [currentUser]);

  if (loading) {
    return <div className="loading">Loading Instruct Schemas...</div>;
  }

  return (
    <div className="instruct-schemas-container">
      <h2>Instruct Schemas</h2>

      <div className="schemas-section">
        <h3>Private Schemas</h3>
        {privateSchemas.length > 0 ? (
          <ul>
            {privateSchemas.map(schema => (
              <li key={schema.id}>
                <strong>{schema.name}</strong> - {schema.access}
                {/* Add buttons or links for actions like Edit, Delete, Load */}
              </li>
            ))}
          </ul>
        ) : (
          <p>No Private Schemas found.</p>
        )}
      </div>

      <div className="schemas-section">
        <h3>Shared Schemas</h3>
        {sharedSchemas.length > 0 ? (
          <ul>
            {sharedSchemas.map(schema => (
              <li key={schema.id}>
                <strong>{schema.name}</strong> - {schema.access}
                {/* Add buttons or links for actions like View, Load */}
              </li>
            ))}
          </ul>
        ) : (
          <p>No Shared Schemas found.</p>
        )}
      </div>

      <div className="schemas-section">
        <h3>Public Schemas</h3>
        {publicSchemas.length > 0 ? (
          <ul>
            {publicSchemas.map(schema => (
              <li key={schema.id}>
                <strong>{schema.name}</strong> - {schema.access}
                {/* Add buttons or links for actions like View, Load */}
              </li>
            ))}
          </ul>
        ) : (
          <p>No Public Schemas found.</p>
        )}
      </div>
    </div>
  );
}

export default InstructSchemas;
