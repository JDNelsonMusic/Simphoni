// src/App.js
import React from 'react';
import { BrowserRouter as Router, Route, Routes, Navigate } from 'react-router-dom';
import Navbar from './components/Navbar';
import PersonaSetup from './components/PersonaSetup';
import ISSetup from './components/ISSetup';
import MyArrays from './components/MyArrays';
import InstructSchemas from './components/InstructSchemas';
import ISThread from './components/ISThread';
import Login from './components/Login';
import Signup from './components/Signup';
import { AuthProvider, useAuth } from './components/AuthProvider';
import { DndProvider } from 'react-dnd';
import { HTML5Backend } from 'react-dnd-html5-backend';
import './App.css';

function PrivateRoute({ children }) {
  const { currentUser } = useAuth();

  if (!currentUser) {
    return <Navigate to="/login" replace />;
  }

  return children;
}

function App() {
  return (
    <AuthProvider>
      <DndProvider backend={HTML5Backend}>
        <Router>
          <Navbar />
          <Routes>
            <Route
              path="/"
              element={
                <PrivateRoute>
                  <PersonaSetup />
                </PrivateRoute>
              }
            />
            <Route
              path="/is-setup"
              element={
                <PrivateRoute>
                  <ISSetup />
                </PrivateRoute>
              }
            />
            <Route
              path="/my-arrays"
              element={
                <PrivateRoute>
                  <MyArrays />
                </PrivateRoute>
              }
            />
            <Route
              path="/instruct-schemas"
              element={
                <PrivateRoute>
                  <InstructSchemas />
                </PrivateRoute>
              }
            />
            <Route
              path="/is-thread"
              element={
                <PrivateRoute>
                  <ISThread />
                </PrivateRoute>
              }
            />
            <Route path="/login" element={<Login />} />
            <Route path="/signup" element={<Signup />} />
          </Routes>
        </Router>
      </DndProvider>
    </AuthProvider>
  );
}

export default App;
