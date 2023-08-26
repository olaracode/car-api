"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Car, Sale

import datetime
#from models import Person

# Hash | Salt
# palabra = a;slkdkfjaslkdjfh8123h1326554;as[]
# Salt es una serie de caracteres secretos que uno agrega a una encriptacion para hacerla mas complicada


# palabra + salt -> asdfjqwe+;laksdhjf
# salt en la aplicacion

salt = "asdf9128"

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])
def handle_hello():

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200

@app.route('/register', methods=['POST'])
def register():
    # email - password
    data = request.get_json() # Recibes informacion
    email = data.get("email", None)
    # NUNCA GUARDAS LA CONTRASEÑA TEXTUAL
    password = data.get("password", None)

    # Encriptamos la contraseña
    hashed_password = generate_password_hash(password)

    new_user = User(email=email, password=hashed_password)
    # REGEX
    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify("Usuario registrado con exito!"), 201 
    except Exception as error:
        db.session.rollback()
        return error, 500

# params(ruta dinamica)
# body -> request.get_json()
# method -> request.method

# POST -> Para crear y recibir informacion

@app.route("/login", methods=['POST'])
def login():
    data = request.get_json()
    email = data.get("email", None)
    password = data.get("password", None)
    
    # existe el usuario actual
    current_user = User.query.filter_by(email=email).first()
    if not current_user:
        return jsonify({"error": "User not found"}), 404

    # Comparamos contraseña
    passwords_match = check_password_hash(current_user.password, password)
    if not passwords_match:
        return jsonify({"error": "Contraseña invalida"}), 401
    
    return jsonify("Loggeado con exito")

@app.route('/cars', methods=['GET'])
def get_cars():
    cars = Car.query.all()
    return jsonify({"cars": [car.serialize() for car in cars]}), 200

@app.route('/car', methods=['POST'])
def create_car():
    data = request.get_json()
    brand = data.get("brand", None)
    model = data.get("model", None)
    year = data.get("year", None)
    price = data.get("price", None)
    user_id = data.get("user_id", None)

    new_car = Car(brand=brand, model=model, year=year, price=price, user_id=user_id)

    try:
        db.session.add(new_car)
        db.session.commit()
        return jsonify({"car": new_car.serialize()}), 201

    except Exception as error:
        db.session.rollback()
        return error, 500

@app.route('/sale/<int:car_id>', methods=['POST'])
def create_sale(car_id):
    # -> precio viene del carro
    # fecha es hoy
    # commision a partir del precio
    # vendedor
    # comprador
    data = request.get_json()
    buyer_id = data.get('buyer_id', None)

    # validar si el carro existe
    current_car = Car.query.get(car_id)

    if not current_car:
        return jsonify({"error": "Car not found"}), 404
    
    buyer_user = User.query.get(buyer_id)

    if not buyer_user:
        return jsonify({"error": "no autorizado"}), 401
    
    current_date = datetime.datetime.now()

    commision = current_car.price * 0.02
    new_sale = Sale(
        price=current_car.price,
        sale_date=current_date,
        commision=commision,
        car_id=car_id,
        seller_id=current_car.user_id,
        buyer_id=buyer_id
    )
    try:
        db.session.add(new_sale)
        db.session.commit()
        return jsonify("Venta realizada con exito"), 201
    except Exception as error:
        db.session.rollback()
        return jsonify(error), 500




# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
