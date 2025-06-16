import os
import psycopg2
import bcrypt
import jwt
from datetime import datetime, timedelta
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Clave secreta para JWT
JWT_SECRET = os.environ.get('JWT_SECRET', 'changeme')

# ------------------------------------------------------------------
#  Conexión a Postgres (local o Railway)
# 
#  1. Si existe la variable de entorno DATABASE_URL (p.ej. en Railway),
#     se usará ese valor.
#  2. En caso contrario, se conectará a tu Postgres local con este DSN:
#     postgresql://<usuario>:<pass>@localhost:5432/<tu_bd>
# ------------------------------------------------------------------
DATABASE_URL = os.environ.get(
    'DATABASE_URL',
    'postgresql://postgres:223013@localhost:5432/railway'
)
conn = psycopg2.connect(DATABASE_URL)
# ------------------------------------------------------------------

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

# UC-07: Registro
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    rut      = data.get('rut', '').strip()
    nombre   = data.get('nombre', '').strip()
    apellido = data.get('apellido', '').strip()
    email    = data.get('email', '').strip().lower()
    password = data.get('password')

    if not all([rut, nombre, apellido, email, password]):
        return jsonify(message='Todos los campos son obligatorios'), 400

    existing = query(
        'SELECT id FROM usuario WHERE email=%s',
        (email,), fetchone=True
    )
    if existing:
        return jsonify(message='Email ya registrado'), 400

    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    query(
        'INSERT INTO usuario (rut,nombre,apellido,email,contrasena,role) '
        'VALUES (%s,%s,%s,%s,%s,%s)',
        (rut, nombre, apellido, email, hashed, 'user'),
        commit=True
    )
    return jsonify(message='Registrado correctamente'), 201

# UC-08: Login
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    email    = data.get('email', '').strip().lower()
    password = data.get('password') or ''

    if not email or not password:
        return jsonify(message='Email y contraseña son obligatorios'), 400

    row = query(
        'SELECT id, contrasena FROM usuario WHERE email=%s',
        (email,), fetchone=True
    )
    if not row:
        return jsonify(message='Credenciales inválidas'), 401

    user_id, hashed = row
    if not bcrypt.checkpw(password.encode(), hashed.encode()):
        return jsonify(message='Credenciales inválidas'), 401

    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(hours=24)
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm='HS256')
    return jsonify(token=token)


# UC-21: Compra → crear orden y actualizar stock
@app.route('/api/purchase', methods=['POST'])
def purchase():
    data = request.get_json() or {}
    user_id = data.get('user_id')
    items = data.get('items', [])
    if not user_id or not items:
        return jsonify(error="user_id e items son obligatorios"), 400

    # Calcular total y validar stock
    total = 0
    for it in items:
        pid, qty = it.get('product_id'), it.get('quantity', 0)
        row = query("SELECT precio, stock FROM producto WHERE id=%s", (pid,), fetchone=True)
        if not row:
            return jsonify(error=f"Producto {pid} no existe"), 404
        precio, stock = row
        if stock < qty:
            return jsonify(error=f"Stock insuficiente para producto {pid}"), 400
        total += float(precio) * qty

    # Crear orden
    order = query(
        "INSERT INTO orden (usuario_id,total) VALUES (%s,%s) RETURNING id",
        (user_id, total),
        fetchone=True, commit=True
    )[0]

    # Detalle y actualizar stock
    for it in items:
        pid, qty = it['product_id'], it['quantity']
        query(
            "INSERT INTO orden_producto (orden_id,producto_id,cantidad) VALUES (%s,%s,%s)",
            (order, pid, qty),
            commit=True
        )
        query(
            "UPDATE producto SET stock = stock - %s WHERE id=%s",
            (qty, pid),
            commit=True
        )

    return jsonify(order_id=order), 201


# UC-23: Favoritos (toggle)
@app.route('/api/favorite', methods=['POST'])
def toggle_favorite():
    data = request.get_json() or {}
    user_id = data.get('user_id')
    prod_id = data.get('product_id')
    if not user_id or not prod_id:
        return jsonify(error="user_id y product_id son obligatorios"), 400

    existing = query(
        "SELECT id FROM favorito WHERE usuario_id=%s AND producto_id=%s",
        (user_id, prod_id),
        fetchone=True
    )
    if existing:
        query("DELETE FROM favorito WHERE id=%s", (existing[0],), commit=True)
        action = 'removed'
    else:
        query(
            "INSERT INTO favorito (usuario_id,producto_id) VALUES (%s,%s)",
            (user_id, prod_id),
            commit=True
        )
        action = 'added'
    return jsonify(action=action), 200


# UC-26: Filtrar catálogo por categorías múltiples
@app.route('/api/products', methods=['GET'])
def list_products():
    cats = request.args.getlist('categoria')  # /api/products?categoria=A&categoria=B
    if cats:
        rows = query(
            "SELECT id,nombre,categoria,precio,stock FROM producto WHERE categoria = ANY(%s)",
            (cats,)
        )
    else:
        rows = query("SELECT id,nombre,categoria,precio,stock FROM producto")
    prods = [
        {
            'id': r[0], 'nombre': r[1], 'categoria': r[2],
            'precio': float(r[3]), 'stock': r[4]
        }
        for r in rows
    ]
    return jsonify(prods)


# UC-29: Carrito digital
@app.route('/api/cart', methods=['GET'])
def get_cart():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify(error="user_id es obligatorio"), 400
    rows = query(
        "SELECT c.producto_id,p.nombre,p.precio,c.cantidad "
        "FROM carrito c JOIN producto p ON c.producto_id=p.id "
        "WHERE c.usuario_id=%s",
        (user_id,)
    )
    cart = [
        {'product_id': r[0], 'nombre': r[1], 'precio': float(r[2]), 'quantity': r[3]}
        for r in rows
    ]
    return jsonify(cart)


@app.route('/api/cart', methods=['POST'])
def add_to_cart():
    data = request.get_json() or {}
    user_id = data.get('user_id')
    prod_id = data.get('product_id')
    qty     = data.get('quantity', 1)
    if not (user_id and prod_id):
        return jsonify(error="user_id y product_id son obligatorios"), 400
    query(
        "INSERT INTO carrito (usuario_id,producto_id,cantidad) VALUES (%s,%s,%s) "
        "ON CONFLICT (usuario_id,producto_id) DO UPDATE SET cantidad = carrito.cantidad + %s",
        (user_id, prod_id, qty, qty),
        commit=True
    )
    return jsonify(message="Añadido al carrito"), 201


@app.route('/api/cart', methods=['DELETE'])
def remove_from_cart():
    data = request.get_json() or {}
    user_id = data.get('user_id')
    prod_id = data.get('product_id')
    if not (user_id and prod_id):
        return jsonify(error="user_id y product_id son obligatorios"), 400
    query("DELETE FROM carrito WHERE usuario_id=%s AND producto_id=%s", (user_id, prod_id), commit=True)
    return jsonify(message="Eliminado del carrito"), 200


# UC-40: Verificar pedido por código
@app.route('/api/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    row = query(
        "SELECT id,usuario_id,total,fecha FROM orden WHERE id=%s",
        (order_id,), fetchone=True
    )
    if not row:
        return jsonify(error="Orden no encontrada"), 404
    order = {'id': row[0], 'user_id': row[1], 'total': float(row[2]), 'fecha': row[3].isoformat()}
    items = query(
        "SELECT producto_id,cantidad FROM orden_producto WHERE orden_id=%s",
        (order_id,)
    )
    order['items'] = [{'product_id': i[0], 'quantity': i[1]} for i in items]
    return jsonify(order)


# UC-42: Añadir producto al catálogo
@app.route('/api/products', methods=['POST'])
def create_product():
    data = request.get_json() or {}
    nombre    = data.get('nombre','').strip()
    categoria = data.get('categoria','').strip()
    precio    = data.get('precio')
    stock     = data.get('stock', 0)
    if not (nombre and precio is not None):
        return jsonify(error="nombre y precio son obligatorios"), 400
    query(
        "INSERT INTO producto (nombre,categoria,precio,stock) VALUES (%s,%s,%s,%s)",
        (nombre, categoria, precio, stock),
        commit=True
    )
    return jsonify(message="Producto creado"), 201


# UC-43: Eliminar producto con confirmación
@app.route('/api/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    query("DELETE FROM producto WHERE id=%s", (product_id,), commit=True)
    return jsonify(message="Producto eliminado"), 200


# UC-45/46: Gestionar permisos de usuario (role: 'user'|'admin')
@app.route('/api/users/<int:user_id>/permissions', methods=['PATCH'])
def update_permissions(user_id):
    data = request.get_json() or {}
    role = data.get('role')
    if role not in ('user', 'admin'):
        return jsonify(error="Role inválido"), 400
    query("UPDATE usuario SET role=%s WHERE id=%s", (role, user_id), commit=True)
    return jsonify(message="Permisos actualizados"), 200


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='127.0.0.1', port=port, debug=True)
