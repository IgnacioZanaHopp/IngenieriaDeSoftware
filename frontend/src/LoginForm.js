// src/LoginForm.js
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

export default function LoginForm({ api, onLogin }) {
  const [form, setForm] = useState({ email: '', password: '' });
  const [error, setError] = useState('');
  const nav = useNavigate();

  const handleChange = e => {
    setForm({ ...form, [e.target.name]: e.target.value });
    setError(''); // limpiar error al escribir
  };

  const handleSubmit = async e => {
    e.preventDefault();

    // A1: Validación de campos vacíos
    if (!form.email || !form.password) {
      setError('Por favor completa todos los campos.');
      return;
    }

    try {
      const res = await fetch(`${api}/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form),
      });
      const data = await res.json();

      if (!res.ok) {
        // A2: Credenciales inválidas
        setError(data.message || 'Email o contraseña incorrectos.');
        return;
      }

      // 5: Éxito → guardamos token y redirigimos
      onLogin(data.token);
      nav('/');
    } catch (e) {
      // E1: Error interno
      setError('Error interno, intenta más tarde.');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="card">
      <h2>Login</h2>

      <input
        name="email"
        type="email"
        placeholder="Email"
        value={form.email}
        onChange={handleChange}
        required
      />

      <input
        name="password"
        type="password"
        placeholder="Contraseña"
        value={form.password}
        onChange={handleChange}
        required
      />

      <button type="submit">Entrar</button>

      {error && <p className="msg error">{error}</p>}
    </form>
  );
}
