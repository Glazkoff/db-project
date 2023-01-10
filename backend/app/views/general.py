import psycopg2.extras
from flask import (
    render_template,
    jsonify,
    make_response,
    abort,
    request,
    redirect,
    Blueprint,
)
from flask_login import login_required, current_user
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

general_blueprint = Blueprint("general", __name__)

API_PREFIX = "/api"


@general_blueprint.route("/")
def home_template():
    conn = get_db()
    cur = conn.cursor()
    last_receipts_req = "SELECT * FROM receipts ORDER BY id DESC LIMIT 10"
    cur.execute(last_receipts_req)
    receipts = cur.fetchall()
    receipts_aggregation_req = "SELECT COUNT(*) FROM receipts;"
    cur.execute(receipts_aggregation_req)
    receipts_aggregation = cur.fetchone()
    close_db()
    return render_template(
        "home.html",
        receipts=receipts,
        aggregation=receipts_aggregation,
    )
