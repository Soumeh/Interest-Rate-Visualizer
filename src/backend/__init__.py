from flask import Flask
from flask.cli import load_dotenv
from flask_sqlalchemy import SQLAlchemy

from src.backend.config import Config
from src.db import Base
from src.frontend.app import create_dash

load_dotenv()
db = SQLAlchemy(model_class=Base)


def create_app():
    server = Flask(__name__)
    server.config.from_object(Config)
    db.init_app(server)

    create_dash(server)
    return server
