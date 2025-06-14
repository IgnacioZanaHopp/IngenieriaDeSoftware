from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Permite llamadas desde tu React

# Ruta de prueba
@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})

# Aquí agregarás tus endpoints: /register, /login, /products, /purchase, etc.

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
