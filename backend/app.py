import os
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Leemos la URL de conexión desde la variable DATABASE_URL
db_url = os.environ.get('DATABASE_URL')
if not db_url:
    raise RuntimeError("La variable de entorno DATABASE_URL no está definida")

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Ejemplo de modelo
class Cliente(db.Model):
    id       = db.Column(db.Integer, primary_key=True)
    nombre   = db.Column(db.String(100), nullable=False)
    email    = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

# Ruta de prueba
@app.route('/api/health')
def health():
    return jsonify(status='ok')

if __name__ == '__main__':
    # Crea las tablas si no existen
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', debug=True)
