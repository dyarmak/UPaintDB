# import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_mail import Mail


app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:SQLftw99@localhost:5432/UPaintDB' 
app.config.from_object(Config)
mail = Mail(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

from ultradb import routes