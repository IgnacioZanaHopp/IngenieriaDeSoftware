// src/Receipt.js
import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';

export default function Receipt({ api, token }) {
  const { orderId } = useParams();
  const [status, setStatus] = useState('loading'); // loading | ok | error_mail | error_general
  const [pdfUrl, setPdfUrl] = useState('');

  useEffect(() => {
    // llamamos a nuestro endpoint que engloba UC-33
    fetch(`${api}/receipt/${orderId}`, {
      method: 'POST', // asume POST que dispara generación/envío
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      }
    })
      .then(async res => {
        if (!res.ok) throw new Error('general');
        const data = await res.json();
        if (data.status === 'ok') {
          setStatus('ok');
        } else if (data.status === 'error_mail') {
          // recibimos también la URL para descarga
          setPdfUrl(data.pdfUrl);
          setStatus('error_mail');
        }
      })
      .catch(() => setStatus('error_general'));
  }, [api, orderId, token]);

  if (status === 'loading') {
    return <p>Generando y enviando tu boleta…</p>;
  }

  if (status === 'error_general') {
    return <p className="msg error">Error interno, intenta más tarde.</p>;
  }

  if (status === 'ok') {
    return <p className="msg success">¡Listo! Boleta enviada a tu correo.</p>;
  }

  // status === 'error_mail'
  return (
    <div>
      <p className="msg error">
        Hubo un problema enviando el email. Puedes descargarla aquí:
      </p>
      {pdfUrl && (
        <a href={pdfUrl} download={`boleta-${orderId}.pdf`}>
          👉 Descargar PDF
        </a>
      )}
    </div>
  );
}
