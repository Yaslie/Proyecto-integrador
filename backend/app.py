from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import MySQLdb.cursors

app = Flask(__name__)
CORS(app)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''  # Cambia esto por tu contraseña real
app.config['MYSQL_DB'] = 'marketplace'
app.config['JWT_SECRET_KEY'] = 'super-secret-key'

mysql = MySQL(app)
jwt = JWTManager(app)

# Registro de usuario
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    cursor = mysql.connection.cursor()
    cursor.execute('INSERT INTO Users (Username, Email, Password, Role) VALUES (%s, %s, %s, %s)',
                   (data['username'], data['email'], data['password'], data.get('role', 'buyer')))
    mysql.connection.commit()
    return jsonify({'msg': 'Usuario registrado'}), 201

# Login tradicional
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM Users WHERE Email=%s AND Password=%s', (data['email'], data['password']))
    user = cursor.fetchone()
    if user:
        access_token = create_access_token(identity=user['UserID'])
        return jsonify(access_token=access_token, user=user)
    return jsonify({'msg': 'Credenciales incorrectas'}), 401

# Obtener productos
@app.route('/products', methods=['GET'])
def get_products():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM Products')
    products = cursor.fetchall()
    return jsonify(products)

# Agregar producto (modo vendedor)
@app.route('/products', methods=['POST'])
@jwt_required()
def add_product():
    data = request.json
    cursor = mysql.connection.cursor()
    cursor.execute('INSERT INTO Products (SellerID, Name, Description, Price, Stock, CategoryID, usuario_creacion) VALUES (%s, %s, %s, %s, %s, %s, %s)',
                   (data['seller_id'], data['name'], data['description'], data['price'], data['stock'], data['category_id'], data['usuario_creacion']))
    mysql.connection.commit()
    return jsonify({'msg': 'Producto agregado'}), 201

# Modificar producto
@app.route('/products/<int:product_id>', methods=['PUT'])
@jwt_required()
def update_product(product_id):
    data = request.json
    cursor = mysql.connection.cursor()
    cursor.execute('UPDATE Products SET Name=%s, Description=%s, Price=%s, Stock=%s, CategoryID=%s, usuario_modificacion=%s WHERE ProductID=%s',
                   (data['name'], data['description'], data['price'], data['stock'], data['category_id'], data['usuario_modificacion'], product_id))
    mysql.connection.commit()
    return jsonify({'msg': 'Producto actualizado'})

# Eliminar producto
@app.route('/products/<int:product_id>', methods=['DELETE'])
@jwt_required()
def delete_product(product_id):
    cursor = mysql.connection.cursor()
    cursor.execute('DELETE FROM Products WHERE ProductID=%s', (product_id,))
    mysql.connection.commit()
    return jsonify({'msg': 'Producto eliminado'})

if __name__ == '__main__':
    app.run(debug=True)