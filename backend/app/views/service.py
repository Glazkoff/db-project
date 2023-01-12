import psycopg2.extras
from flask import render_template, request, abort, redirect, Blueprint
from flask_login import login_required
from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    SelectField,
    TextAreaField,
    IntegerField,
    FieldList,
    FormField,
    ValidationError,
)
from wtforms.validators import DataRequired
from ..db import get_db, close_db
from .general import API_PREFIX

service_blueprint = Blueprint("service", __name__)


@service_blueprint.route("/error")
def error_view():
    return render_template("error.html")


@service_blueprint.route("/success")
def success_view():
    return render_template("success.html")
