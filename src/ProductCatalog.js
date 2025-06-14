import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

export default function ProductCatalog({ api, token }) {
  const [products, setProducts]     = useState([]);
  const [categories, setCategories] = useState([]);
  const [filtros, setFiltros]       = useState([]);
  const nav = useNavigate();

  // 1) traer categorías
  useEffect(() => {
    fetch(`${api}/categories`)
      .then(r=>r.json())
      .then(setCategories);
  },[api]);

  // 2) traer productos cada vez que cambian filtros
  useEffect(() => {
    const qs = filtros.length
      ? `?categories=${filtros.join(',')}`
      : '';
    fetch(`${api}/products${qs}`)
      .then(r=>r.json())
      .then(setProducts);
  }, [api, filtros]);

  const toggleFiltro = cat => {
    setFiltros(f =>
      f.includes(cat)
        ? f.filter(x=>x!==cat)
        : [...f, cat]
    );
  };

  const addToFav = async id => {
    if (!token) return alert('Haz login primero');
    await fetch(`${api}/favorites`, {
      method:'POST',
      headers:{
        'Content-Type':'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ productId:id })
    });
    // podrías indicar con un mensaje o cambiar icono en UI
  };

  const handlePurchase = async (productId) => {
    if (!token) return alert('Haz login primero');
    const res = await fetch(`${api}/purchase`, {
      method:'POST',
      headers:{
        'Content-Type':'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ productId, quantity: 1 })
    });
    const data = await res.json();
    if (res.ok) {
      // 21) actualizar stock en frontend
      setProducts(ps =>
        ps.map(p =>
          p.id === productId
            ? { ...p, stock: p.stock - 1 }
            : p
        )
      );
      // 33) navegar a PDF de boleta
      nav(`/receipt/${data.orderId}`);
    } else {
      alert(data.message || 'Error al comprar');
    }
  };

  return (
    <div>
      <h2>Catálogo</h2>

      <div className="filtros">
        <strong>Filtrar por categorías:</strong>
        {categories.map(c=>(
          <label key={c}>
            <input
              type="checkbox"
              checked={filtros.includes(c)}
              onChange={()=>toggleFiltro(c)}
            />
            {c}
          </label>
        ))}
      </div>

      <div className="grid">
        {products.map(p=>(
          <div className="card producto" key={p.id}>
            <h3>{p.name}</h3>
            <p>Stock: {p.stock}</p>
            <button onClick={()=>handlePurchase(p.id)}>
              Comprar 1
            </button>{' '}
            <button onClick={()=>addToFav(p.id)}>
              {p.isFavorite ? '💖' : '🤍'}
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
