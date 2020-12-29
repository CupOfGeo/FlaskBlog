from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app) #database duh CHAPTER 4 to upgrade/change
migrate = Migrate(app, db) #migrate engine (?)

login = LoginManager(app) #login Chapter 5
login.login_view = 'login' #endpointthe name used in url_for'login'

#models = db model
from app import routes, models
