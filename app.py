from flask import Flask
from os import getenv

app = Flask(__name__)
app.run(debug=True)
app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = getenv("SECRET_KEY")

import routes
from utils import populate_db
populate_db.insert_stops()