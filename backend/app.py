import os
import psycopg2
import bcrypt
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Conexión al pool de Postgres
DATABASE_URL = os.environ.get(
    'DATABASE_URL',
    'postgresql://postgres:223013@localhost:5432/railway'
)
conn = psycopg2.connect(DATABASE_URL)

def query(sql, params=(), fetchone=False, commit=False):
    with conn.cursor() as cur:
        cur.execute(sql, params)
        if commit:
            conn.commit()
        if sql.strip().upper().startswith("SELECT"):
            return cur.fetchone() if fetchone else cur.fetchall()

@app.route('/api/health')
def health():
    return jsonify(status='ok')

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    nombre   = data.get('nombre','').strip()
    email    = data.get('email','').strip().lower()
    password = data.get('password','')
    if not (nombre and email and password):
        return jsonify(error="Todos los campos son obligatorios"), 400

    # Hasheo de contraseña
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    try:
        query(
            "INSERT INTO usuario(nombre,email,password) VALUES (%s,%s,%s)",
            (nombre, email, hashed),
            commit=True
        )
    except psycopg2.errors.UniqueViolation:
        return jsonify(error="Email ya registrado"), 409

    return jsonify(message="Usuario creado correctamente"), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    email    = data.get('email','').strip().lower()
    password = data.get('password','')
    if not (email and password):
        return jsonify(error="Email y contraseña son obligatorios"), 400

    row = query(
        "SELECT id,password FROM usuario WHERE email=%s",
        (email,),
        fetchone=True
    )
    if not row:
        return jsonify(error="Usuario no encontrado"), 404

    user_id, hashed = row
    if not bcrypt.checkpw(password.encode(), hashed.encode()):
        return jsonify(error="Credenciales inválidas"), 401

    return jsonify(message="Autenticación exitosa", user_id=user_id), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='127.0.0.1', port=port, debug=True)
