from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager

# initialize the database 
db = SQLAlchemy()
DB_NAME = "database.db"

# flask application 
def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'yidan' # the secret key of the server cookie/session 
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}' # db is stored at this location 
    db.init_app(app) # initialize

    # import files 
    from .views import views
    from .auth import auth
    #register 
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/') # nothing for prefix
    
    # import user class defined in the __init__
    from .models import User
    
    with app.app_context():
        db.create_all()
    # manage login 
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login' # direct if not login 
    login_manager.init_app(app) # initialization 
    
    # how we load a User
    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app

# create the database (if not exists)
def create_database(app):
    if not path.exists('website/' + DB_NAME):
        db.create_all(app=app)
      