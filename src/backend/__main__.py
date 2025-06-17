from os import getenv

from flask import Flask
from flask.cli import load_dotenv
from flask_sqlalchemy import SQLAlchemy

from src.backend.config import Config
from src.db import Base
from src.frontend.app import create_dash

load_dotenv()

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(model_class=Base)
db.init_app(app)

create_dash(app, db)

DEBUG = getenv("FLASK_DEBUG", False)

if __name__ == "__main__":
	app.run(debug=DEBUG)
