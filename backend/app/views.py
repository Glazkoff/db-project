import psycopg2.extras
from flask import render_template, jsonify, make_response, abort, request, redirect
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
from app import app
from .db import get_db, close_db

API_PREFIX = "/api"


@app.route("/")
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


@app.route("/receipt/<int:id>")
def receipt_detalization_view(id):
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    receipt_req = "SELECT * FROM receipts WHERE id = (%s)"
    cur.execute(receipt_req, (id,))
    receipt = cur.fetchone()
    categories_hierarchy_req = """
        WITH RECURSIVE category_chain (id, category_name, parent_category_id) AS (
        SELECT id,
            category_name,
            parent_category_id
        FROM categories
        WHERE id = (%s)
        UNION ALL
        SELECT c.id,
            c.category_name,
            c.parent_category_id
        FROM categories c
            JOIN category_chain cc ON cc.parent_category_id = c.id
        )
        SELECT *
        FROM category_chain;
    """
    cur.execute(categories_hierarchy_req, (id,))
    categories_hierarchy = cur.fetchall()
    close_db()
    return render_template(
        "receipt.html", receipt=receipt, categories=categories_hierarchy
    )


@app.route("/receipt/update/<int:id>")
@login_required
def receipt_update_view(id):
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    req = "SELECT * FROM receipts WHERE id = (%s)"
    cur.execute(req, (id,))
    receipt = cur.fetchone()
    close_db()
    return render_template("update_receipt.html", receipt=receipt)


@app.put(f"{API_PREFIX}/receipt/<int:id>")
@login_required
def update_receipt(id):
    conn = get_db()
    cur = conn.cursor()
    req = "UPDATE receipts SET title = %s, body = %s WHERE id = (%s)"
    title = request.form.get("title", "")
    body = request.form.get("body", "")
    cur.execute(
        req,
        (
            title,
            body,
            id,
        ),
    )
    rows_updated = cur.rowcount
    conn.commit()
    close_db()
    if rows_updated > 0:
        return make_response(
            jsonify({"message": "Успешно обновлено", "success": True}), 200
        )
    else:
        return make_response(
            jsonify({"message": "Произошла ошибка", "success": False}), 400
        )


@app.delete(f"{API_PREFIX}/receipt/<int:id>")
@login_required
def delete_receipt(id):
    conn = get_db()
    cur = conn.cursor()
    req = "DELETE FROM receipts WHERE id = (%s)"
    cur.execute(req, (id,))
    rows_deleted = cur.rowcount
    conn.commit()
    close_db()
    if rows_deleted > 0:
        return make_response(
            jsonify({"message": "Успешно удалено", "success": True}), 200
        )
    else:
        return make_response(
            jsonify({"message": "Произошла ошибка", "success": False}), 400
        )


@app.route("/add_receipt")
@login_required
def add_receipt_view():
    def get_categories():
        categories = []
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

    def validate_ingredient_name(form, field):
        conn = None
        try:
            conn = get_db()
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM ingredients WHERE name=%s", (field.data,))
            count = cur.fetchone()[0]
            if count > 0:
                raise ValidationError("Ингредиент уже существует")
        except Exception as e:
            raise ValidationError(str(e))
        finally:
            close_db()

    class IngredientForm(FlaskForm):
        name = StringField(
            "Name",
            validators=[DataRequired(), validate_ingredient_name],
        )
        unit = SelectField("Unit", coerce=int)
        amount = IntegerField("Amount", validators=[DataRequired()])
        comment = StringField("Comment")

    class ReceiptForm(FlaskForm):
        title = StringField("Название", validators=[DataRequired()])
        body = TextAreaField("Текст рецепта", validators=[DataRequired()])
        category = SelectField("Категории", coerce=int, choices=get_categories())
        ingredients = FieldList(FormField(IngredientForm))

    form = ReceiptForm()
    return render_template("add_receipt.html", form=form)


@app.post(f"{API_PREFIX}/add_receipt")
@login_required
def add_receipt():
    conn = get_db()
    cur = conn.cursor()
    title = request.form.get("title", "")
    body = request.form.get("body", "")
    category_id = request.form.get("category", "")
    user_id = current_user.id
    cur.execute(
        "INSERT INTO receipts (title, body, author_id, category_id) VALUES (%s, %s, %s, %s) RETURNING id",
        (title, body, user_id, category_id),
    )
    rows_affected = cur.rowcount
    conn.commit()
    close_db()
    if rows_affected > 0:
        return redirect("/")
    else:
        abort(500)
