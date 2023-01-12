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

admin_blueprint = Blueprint("admin", __name__)


@admin_blueprint.route("/admin")
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


@admin_blueprint.route("/admin/dashboard")
@login_required
def admin_dashboard_view():
    dashboard_data = {}
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    # подсчёт пользователей
    users_count_req = "SELECT COUNT(*) FROM users;"
    cur.execute(users_count_req)
    dashboard_data["users_count"] = cur.fetchone()["count"]

    # среднее количество ингредиентов
    ingredients_avg_count_req = """
      SELECT AVG(cnt) FROM (
        SELECT receipt_id, COUNT(*) AS cnt FROM ingredients_in_receipts GROUP BY receipt_id
      ) subquery;
    """
    cur.execute(ingredients_avg_count_req)
    dashboard_data["ingredients_avg_count"] = cur.fetchone()

    # 5 пользователей, создавших больше всего рецептов:
    most_active_users_req = """
      SELECT users.name, COUNT(*) FROM receipts
      JOIN users ON receipts.author_id = users.id
      GROUP BY users.name ORDER BY COUNT(*) DESC LIMIT 5;
    """
    cur.execute(most_active_users_req)
    dashboard_data["most_active_users"] = cur.fetchall()

    # наиболее популярный ингредиент и количество раз, когда он используется во всех рецептах:
    most_poular_ingredient_req = """
      SELECT ingredient_name, COUNT(*) FROM ingredients_in_receipts
      JOIN ingredients ON ingredients_in_receipts.ingredient_id = ingredients.id
      GROUP BY ingredient_name ORDER BY COUNT(*) DESC LIMIT 1;
    """
    cur.execute(most_poular_ingredient_req)
    dashboard_data["most_poular_ingredient"] = cur.fetchall()

    # общее количество различных ингредиентов, используемых во всех рецептах:
    distinct_ingredients_count_req = """
      SELECT COUNT(DISTINCT ingredient_id) FROM ingredients_in_receipts;
    """
    cur.execute(distinct_ingredients_count_req)
    dashboard_data["distinct_ingredients_count"] = cur.fetchall()

    # общее количество созданных рецептов в каждом месяце за последний год:
    receipts_count_per_month_last_year_req = """
      SELECT DATE_TRUNC('month', created_at) as month, COUNT(*) FROM receipts
      WHERE created_at >= DATE_TRUNC('month', NOW()) - INTERVAL '1 year'
      GROUP BY month ORDER BY month;
    """
    cur.execute(receipts_count_per_month_last_year_req)
    dashboard_data["receipts_count_per_month_last_year"] = cur.fetchall()

    # среднее количество символов в тексте всех рецептов для каждой категории:
    receipt_text_avg_length_req = """
      SELECT categories.category_name, AVG(LENGTH(body)) FROM receipts
      JOIN categories ON receipts.category_id = categories.id
      GROUP BY categories.category_name;
    """
    cur.execute(receipt_text_avg_length_req)
    dashboard_data["receipt_text_avg_length"] = cur.fetchall()

    close_db()
    return render_template(
        "admin_dashboard.html",
        dashboard_data=dashboard_data,
    )
