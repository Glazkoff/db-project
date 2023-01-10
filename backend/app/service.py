import psycopg2.extras
from flask import render_template, request, abort, redirect
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
from app import app
from .db import get_db, close_db
from .views import API_PREFIX


@app.route("/error")
def error_view():
    return render_template("error.html")


@app.route("/success")
def success_view():
    return render_template("success.html")


@app.errorhandler(404)
def not_found(error):
    return render_template("404.html"), 404


@app.route("/admin")
@login_required
def admin_view():
    class IngredientCreationForm(FlaskForm):
        ingredient_name = StringField(
            "Название",
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
    )


@app.post(f"{API_PREFIX}/admin/ingredients")
@login_required
def add_ingredient():
    conn = get_db()
    cur = conn.cursor()
    ingredient_name = request.form.get("ingredient_name", "")
    cur.execute(
        "INSERT INTO ingredients (ingredient_name) VALUES (%s) RETURNING id",
        (ingredient_name,),
    )
    rows_affected = cur.rowcount
    conn.commit()
    close_db()
    if rows_affected > 0:
        return redirect("/admin")
    else:
        abort(500)
