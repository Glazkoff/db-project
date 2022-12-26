from flask import render_template, jsonify
from app import app


@app.route("/")
def home():
    return "hello world!"


@app.route("/home")
def home_template():
    return render_template("home.html")


@app.route("/test")
def hello_world():
    return jsonify(hello="world")
