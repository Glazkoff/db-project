from flask import Flask
from .db import init_db

app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False
app.config["SECRET_KEY"] = "$5cr5t_k5y"
from app import auth
from app import views


@app.before_first_request
def init():
    init_db()
