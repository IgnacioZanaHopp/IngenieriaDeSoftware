import os
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy     # <-- eliminar
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Leemos la URL de conexión desde DATABASE_URL…
db_url = os.environ.get('DATABASE_URL')
if not db_url:
    raise RuntimeError("La variable de entorno DATABASE_URL no está definida")

app.config['SQLALCHEMY_DATABASE_URI'] = db_url   # <-- eliminar
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # <-- eliminar

db = SQLAlchemy(app)  # <-- eliminar

# Ruta de prueba
@app.route('/api/health')
def health():
    return jsonify(status='ok')

if __name__ == '__main__':
    # Crea las tablas si no existen
    with app.app_context():
        db.create_all()    # <-- eliminar
    app.run(host='0.0.0.0', debug=True)
