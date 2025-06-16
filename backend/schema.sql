CREATE TABLE IF NOT EXISTS usuario (
    id SERIAL PRIMARY KEY,
    rut TEXT NOT NULL,
    nombre TEXT NOT NULL,
    apellido TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    contrasena TEXT NOT NULL,
    role TEXT DEFAULT 'user'
);
