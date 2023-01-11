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


@service_blueprint.route("/admin")
@login_required
def admin_view():
    def get_categories():
        categories = []
        categories.append((0, "Нет родительской категории"))
        try:
            conn = get_db()
            cur = conn.cursor()
            cur.execute("SELECT id, category_name FROM categories")
            rows = cur.fetchall()
            for row in rows:
                categories.append((row[0], row[1]))
        except Exception as e:
            raise ValidationError(str(e))
        finally:
            close_db()
        return categories

    class CategoryCreationForm(FlaskForm):
        category_name = StringField(
            "Название",
            validators=[DataRequired()],
        )
        parent_category_id = SelectField(
            "Родительская категория", coerce=int, choices=get_categories(), default=None
        )

    class IngredientCreationForm(FlaskForm):
        ingredient_name = StringField(
            "Название",
            validators=[DataRequired()],
        )

    class UnitCreationForm(FlaskForm):
        short_name = StringField(
            "Короткое название",
            validators=[DataRequired()],
        )
        full_name = StringField(
            "Полное название",
            validators=[DataRequired()],
        )

    dashboard_data = {}
    content_data = {}
    average_ingredients_count_req = """
        SELECT AVG(num_ingredients) AS avg_ingredients 
        FROM (SELECT COUNT(ingredients_in_receipts.id) AS num_ingredients 
        FROM ingredients_in_receipts 
        GROUP BY ingredients_in_receipts.receipt_id) 
        AS ingredients_count;
    """
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(average_ingredients_count_req)
    dashboard_data["average_ingredients_count"] = cur.fetchone()["avg_ingredients"]
    categories_req = "SELECT * FROM categories ORDER BY id DESC"
    cur.execute(categories_req)
    content_data["categories"] = cur.fetchall()
    ingredients_req = "SELECT * FROM ingredients ORDER BY id DESC"
    cur.execute(ingredients_req)
    content_data["ingredients"] = cur.fetchall()
    units_req = "SELECT * FROM units ORDER BY id DESC"
    cur.execute(units_req)
    content_data["units"] = cur.fetchall()
    close_db()
    return render_template(
        "admin.html",
        dashboard_data=dashboard_data,
        content_data=content_data,
        ingredient_creation_form=IngredientCreationForm(),
        unit_creation_form=UnitCreationForm(),
        category_creation_form=CategoryCreationForm(),
    )
