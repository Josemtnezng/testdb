"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
# Se importan los modelos necesarios para las rutas de autenticación
from models import db, User, UserProfile 
# Se importan las librerías de seguridad
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, JWTManager

app = Flask(__name__)
app.url_map.strict_slashes = False

# --- Configuración de la Base de Datos ---
db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# --- Inicialización de Extensiones ---
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)
bcrypt = Bcrypt(app) # Inicializa Bcrypt

# --- Configuración de JWT ---
# Asegúrate de tener JWT_SECRET en tu archivo .env
app.config["JWT_SECRET_KEY"] = os.environ.get('JWT_SECRET') 
jwt = JWTManager(app)


# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

# --- RUTAS DE AUTENTICACIÓN ---

@app.route('/api/register', methods=['POST'])
def register_user():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    name = data.get('name')

    if not email or not password or not name:
        return jsonify({"msg": "Nombre, email y contraseña son requeridos"}), 400

    user_exists = User.query.filter_by(email=email).first()
    if user_exists:
        return jsonify({"msg": "El correo ya está en uso"}), 409

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = User(name=name, email=email, password_hash=hashed_password)
    new_user.profile = UserProfile() 
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"msg": "Usuario creado exitosamente"}), 201

@app.route('/api/login', methods=['POST'])
def login_user():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"msg": "Email y contraseña son requeridos"}), 400

    user = User.query.filter_by(email=email).first()
    # Se comprueba que el usuario existe Y que la contraseña encriptada coincide
    if user and bcrypt.check_password_hash(user.password_hash, password):
        # Se convierte el user.id (que es un número) a un string
        access_token = create_access_token(identity=str(user.id))
        return jsonify(access_token=access_token)
    
    return jsonify({"msg": "Credenciales incorrectas"}), 401

@app.route('/api/logout', methods=['POST'])
@jwt_required() # Ruta protegida, requiere un token válido
def logout_user():
    #  lógica de logout al borrar el token.
    #  endpoint que  sirve para confirmación y futuras implementaciones.
    return jsonify({"msg": "Logout exitoso"}), 200


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)