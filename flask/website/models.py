from . import db # sql alchomy object 
from flask_login import UserMixin

# user db contains an id, email, password 
# type, key
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True) #unique and non-empty 
    email = db.Column(db.String(150), unique=True) #unique -> two users cannot have the same email
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
