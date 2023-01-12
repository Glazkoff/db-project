from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from .db import init_db
from .views.service import service_blueprint
from .views.general import general_blueprint
from .views.ingredients import ingredients_blueprint
from .views.receipts import receipts_blueprint
from .views.units import units_blueprint
from .views.categories import categories_blueprint
from .views.admin import admin_blueprint

app = Flask(__name__)
Bootstrap(app)
app.config["JSON_AS_ASCII"] = False
app.config["SECRET_KEY"] = "$5cr5t_k5y"
app.register_blueprint(service_blueprint)
app.register_blueprint(general_blueprint)
app.register_blueprint(ingredients_blueprint)
app.register_blueprint(receipts_blueprint)
app.register_blueprint(units_blueprint)
app.register_blueprint(categories_blueprint)
app.register_blueprint(admin_blueprint)
from app import auth


@app.before_first_request
def init():
    init_db()


@app.errorhandler(404)
def not_found(error):
    return render_template("404.html"), 404
