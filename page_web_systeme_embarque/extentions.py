from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS

app = Flask(__name__)

app.config.from_object("config")

db = SQLAlchemy()
migrate = Migrate()
CORS(app)