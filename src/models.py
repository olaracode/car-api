from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), unique=False, nullable=False)
    # cars = db.relationship()

    cars = db.relationship("Car", backref="user", lazy=True)


    shopping_carts = db.relationship("ShoppingCart", backref="user", lazy=True)
    def __repr__(self):
        return '<User %r>' % self.email

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            # do not serialize the password, its a security breach
        }

class Car(db.Model):
    """
    Car(Marca, Modelo, Año, Color, Kilometraje, Precio, Descripcion)
    Relaciones(User, Sales, ShoppingCart)
    """
    id = db.Column(db.Integer, primary_key=True)
    brand = db.Column(db.String(50), unique=False, nullable=False)
    model = db.Column(db.String(50), unique=False, nullable=False)
    year = db.Column(db.Integer, unique=False, nullable=False)
    price = db.Column(db.Integer, unique=False, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)


    shopping_carts = db.relationship("ShoppingCart", backref="car", lazy=True)
    sale = db.relationship("Sale", backref="car")

    def __repr__(self):
        return f"<Car {self.brand} {self.model} - {self.year}>"

    def serialize(self):
        return {
            "id": self.id,
            "brand": self.brand,
            "model": self.model,
            "year": self.year,
            "price": self.price
        }
class Sale(db.Model):
    # Campos
    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer)
    sale_date = db.Column(db.Date)
    commision = db.Column(db.Integer)
    
    # Claves foraneas
    car_id = db.Column(db.Integer, db.ForeignKey("car.id"), nullable=False)

    # 2 relaciones con la misma table
    # Las claves foraneas
    # seller_id -> el vendedor
    seller_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False) 
    # buyer_id -> que compro
    buyer_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    # 2 relaciones con la tabla usuario
    seller = db.relationship("User",  foreign_keys=[seller_id]) #
    purchaser = db.relationship("User", foreign_keys=[buyer_id]) #
    def __repr__(self):
        return f"<Sale {self.price} {self.sale_date}>"
    
    def serialize(self):
        return {
            "id": self.id,
            "price": self.price,
            "sale_date": self.sale_date,
            "commision": self.commision
        }
class ShoppingCart(db.Model):
    """
    Relaciones(User, Car)
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    car_id = db.Column(db.Integer, db.ForeignKey("car.id"), nullable=False)
    
    def __repr__(self):
        return f"<ShoppingCart {self.id}>"
    
    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "car_id": self.car_id
        }