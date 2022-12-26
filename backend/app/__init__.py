from flask import Flask
from .db import init_db

app = Flask(__name__)

from app import views


@app.before_first_request
def init():
    init_db()
