// src/Receipt.js
import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { API } from './api';

export default function Receipt() {
  const { id } = useParams();
  const [order, setOrder] = useState(null);

  useEffect(() => {
    fetch(`${API}/orders/${id}`)
      .then(res => res.json())
      .then(setOrder)
      .catch(console.error);
  }, [id]);

  if (!order) return <p>Cargando recibo...</p>;

  return (
    <div className="receipt">
      <h2>Recibo #{order.id}</h2>
      <p>Fecha: {new Date(order.fecha).toLocaleString()}</p>
      <p>Total: ${order.total}</p>
      <ul>
        {order.items.map(item => (
          <li key={item.id}>
            {item.nombre} × {item.cantidad} = ${item.precio_unit * item.cantidad}
          </li>
        ))}
      </ul>
    </div>
  );
}
