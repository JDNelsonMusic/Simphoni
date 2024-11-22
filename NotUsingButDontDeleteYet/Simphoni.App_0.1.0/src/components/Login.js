// src/components/Login.js
import React, { useRef, useState } from 'react';
import { useAuth } from './AuthProvider';
import { Link, useNavigate } from 'react-router-dom';
import './Auth.css';

function Login() {
  const emailRef = useRef();
  const passwordRef = useRef();
  const { login } = useAuth();
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  async function handleSubmit(e) {
    e.preventDefault();

    try {
      setError('');
      setLoading(true);
      await login(emailRef.current.value, passwordRef.current.value);
      navigate('/');
    } catch {
      setError('Failed to log in');
    }

    setLoading(false);
  }

  return (
    <div className="auth-container">
      <h2>Log In</h2>
      {error && <div className="error-msg">{error}</div>}
      <form onSubmit={handleSubmit} className="auth-form">
        <label>Email</label>
        <input type="email" ref={emailRef} required />

        <label>Password</label>
        <input type="password" ref={passwordRef} required />

        <button disabled={loading} type="submit">Log In</button>
      </form>
      <div className="auth-footer">
        Need an account? <Link to="/signup">Sign Up</Link>
      </div>
    </div>
  );
}

export default Login;
