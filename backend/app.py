import os 
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy      # ← borrar esta línea
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Usa la URL de Railway para conectar a Postgres
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)                         # ← borrar esta línea
# Ejemplo de modelo
class Cliente(db.Model):                     # ← borrar toda la definición de la clase
    id       = db.Column(db.Integer, primary_key=True)
    nombre   = db.Column(db.String(100), nullable=False)
    email    = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

# Ruta de prueba
@app.route('/api/health')
def health():
    return jsonify(status='ok')

if __name__ == '__main__':
    # Si no usas Flask-Migrate, crea las tablas al arrancar:
    with app.app_context():
        db.create_all()                       # ← borrar esta línea
    app.run(host='0.0.0.0', debug=True)
