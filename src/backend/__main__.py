from flask import Flask
from flask.cli import load_dotenv
from flask_sqlalchemy import SQLAlchemy

from src.backend.config import Config
from src.db import Base
from src.frontend.app import create_dash

app = Flask(__name__)
load_dotenv()
db = SQLAlchemy(model_class=Base)

if __name__ == "__main__":
	app.config.from_object(Config)
	db.init_app(app)

	create_dash(app, db)
	app.run(debug=True)
