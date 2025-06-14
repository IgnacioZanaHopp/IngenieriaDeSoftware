import React, { useState } from 'react';
import { Routes, Route, Link, useNavigate } from 'react-router-dom';
import RegistrationForm from './RegistrationForm';
import LoginForm from './LoginForm';
import ProductCatalog from './ProductCatalog';
import Receipt from './Receipt';

const API = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

function App() {
  const [token, setToken] = useState(localStorage.getItem('token'));
  const navigate = useNavigate();

  const handleLogin = (jwt) => {
    localStorage.setItem('token', jwt);
    setToken(jwt);
    navigate('/catalogo');
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    setToken(null);
    navigate('/login');
  };

  return (
    <div className="App">
      <nav>
        <Link to="/">Inicio</Link> |{' '}
        {token
          ? <>
              <Link to="/catalogo">Catálogo</Link> | 
              <button onClick={handleLogout}>Cerrar sesión</button>
            </>
          : <>
              <Link to="/login">Login</Link> | 
              <Link to="/registro">Registro</Link>
            </>
        }
      </nav>

      <Routes>
        <Route path="/" element={<h1>Bienvenido</h1>} />
        <Route path="/registro" element={<RegistrationForm api={API} />} />
        <Route path="/login" element={<LoginForm api={API} onLogin={handleLogin} />} />
        <Route path="/catalogo" element={<ProductCatalog api={API} token={token} />} />
        <Route path="/receipt/:orderId" element={<Receipt api={API} token={token} />} />
      </Routes>
    </div>
  );
}

export default App;
