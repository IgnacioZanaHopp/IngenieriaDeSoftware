import React, { useState } from 'react';

export default function RegistrationForm({ api }) {
  const [form, setForm] = useState({
    rut: '',
    nombre: '',
    apellido: '',
    email: '',
    password: '',
    passwordConfirm: ''
  });
  const [msg, setMsg] = useState({ text:'', type:'success' });

  const handleChange = e => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async e => {
    e.preventDefault();
    // Validación cliente (antes de enviar)
    if (form.password !== form.passwordConfirm) {
      setMsg({ text: 'Las contraseñas no coinciden', type: 'error' });
      return;
    }
    // Llamada al backend
    try {
      const res = await fetch(`${api}/register`, {
        method: 'POST',
        headers: { 'Content-Type':'application/json' },
        body: JSON.stringify(form),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.message || 'Error al registrar');
      setMsg({ text: 'Registrado con éxito 🎉 Inicia sesión.', type: 'success' });
    } catch (err) {
      setMsg({ text: err.message, type: 'error' });
    }
  };

  return (
    <form onSubmit={handleSubmit} className="card">
      <h2>Registro</h2>
      <input name="rut"             placeholder="RUT"              onChange={handleChange} value={form.rut}            required />
      <input name="nombre"          placeholder="Nombre"           onChange={handleChange} value={form.nombre}         required />
      <input name="apellido"        placeholder="Apellido"         onChange={handleChange} value={form.apellido}       required />
      <input name="email"           placeholder="Email"            type="email"      onChange={handleChange} value={form.email}          required />
      <input name="password"        placeholder="Contraseña"       type="password"   onChange={handleChange} value={form.password}       required />
      <input name="passwordConfirm" placeholder="Repite Contraseña" type="password"  onChange={handleChange} value={form.passwordConfirm}required />
      <button type="submit">Crear cuenta</button>
      {msg.text && (
        <p className={`msg ${msg.type==='error'?'error':''}`}>{msg.text}</p>
      )}
    </form>
  );
}