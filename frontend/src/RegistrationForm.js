// src/RegistrationForm.js
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { API } from './api';

export default function RegistrationForm() {
  const navigate = useNavigate();
  const [nombre, setNombre] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async e => {
    e.preventDefault();
    try {
      const res = await fetch(`${API}/users`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ nombre, email, password })
      });
      if (!res.ok) throw new Error('Registro fallido');
      navigate('/login');
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="form-container">
      <h2>Registro</h2>
      <form onSubmit={handleSubmit}>
        <input
          value={nombre}
          onChange={e => setNombre(e.target.value)}
          placeholder="Nombre"
          required
        />
        <input
          type="email"
          value={email}
          onChange={e => setEmail(e.target.value)}
          placeholder="Email"
          required
        />
        <input
          type="password"
          value={password}
          onChange={e => setPassword(e.target.value)}
          placeholder="Password"
          required
        />
        <button type="submit">Crear cuenta</button>
      </form>
      {error && <p className="error">{error}</p>}
    </div>
  );
}
