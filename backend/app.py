import os
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Ruta de prueba
@app.route('/api/health')
def health():
    return jsonify(status='ok')

if __name__ == '__main__':
    # Inicia el servidor
    app.run(host='0.0.0.0', port=8080, debug=True)
