// src/App.js
import React from 'react';
import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom';
import ProductCatalog from './ProductCatalog';
import LoginForm from './LoginForm';
import RegistrationForm from './RegistrationForm';
import Receipt from './Receipt';
import './styles.css';

export default function App() {
  return (
    <BrowserRouter>
      <nav className="main-nav">
        <NavLink to="/">Inicio</NavLink>
        <NavLink to="/login">Login</NavLink>
        <NavLink to="/register">Registro</NavLink>
      </nav>
      <main>
        <Routes>
          <Route path="/" element={<ProductCatalog />} />
          <Route path="/login" element={<LoginForm />} />
          <Route path="/register" element={<RegistrationForm />} />
          <Route path="/recibo/:id" element={<Receipt />} />
        </Routes>
      </main>
    </BrowserRouter>
  );
}
