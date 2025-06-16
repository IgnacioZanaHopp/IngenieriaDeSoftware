// src/ProductCatalog.js
import React, { useEffect, useState } from 'react';
import { API } from './api';

export default function ProductCatalog() {
  const [products, setProducts] = useState([]);

  useEffect(() => {
    fetch(`${API}/products`)
      .then(res => res.json())
      .then(setProducts)
      .catch(console.error);
  }, []);

  return (
    <div className="catalog">
      <h2>Catálogo de Productos</h2>
      <ul>
        {products.map(p => (
          <li key={p.id} className="product-card">
            <h3>{p.nombre}</h3>
            <p>{p.descripcion}</p>
            <p>Precio: ${p.precio}</p>
            <p>Stock: {p.stock}</p>
          </li>
        ))}
      </ul>
    </div>
  );
}
