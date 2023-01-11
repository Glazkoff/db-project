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
from .general import API_PREFIX

categories_blueprint = Blueprint("categories", __name__)

# CREATE API
@categories_blueprint.post(f"{API_PREFIX}/categories")
@login_required
def add_category():
    conn = get_db()
    cur = conn.cursor()
    category_name = request.form.get("category_name", "")
    parent_category_id = request.form.get("parent_category_id", 0)
    if int(parent_category_id) == 0:
        parent_category_id = None
    cur.execute(
        "INSERT INTO categories (category_name, parent_category_id) VALUES (%s, %s) RETURNING id",
        (category_name, parent_category_id),
    )
    rows_affected = cur.rowcount
    conn.commit()
    close_db()
    if rows_affected > 0:
        return redirect("/admin?tab=categories")
    else:
        abort(500)


# UPDATE API
@categories_blueprint.put(f"{API_PREFIX}/categories/<int:id>")
@login_required
def update_category(id):
    conn = get_db()
    cur = conn.cursor()
    req = "UPDATE categories SET category_name = %s, parent_category_id = %s WHERE id = (%s)"
    category_name = request.form.get("category_name", "")
    parent_category_id = request.form.get("parent_category_id", 0)
    if int(parent_category_id) == 0:
        parent_category_id = None
    cur.execute(
        req,
        (
            category_name,
            parent_category_id,
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


# DELETE API
@categories_blueprint.delete(f"{API_PREFIX}/categories/<int:id>")
@login_required
def delete_category(id):
    conn = get_db()
    cur = conn.cursor()
    req = "DELETE FROM categories WHERE id = (%s)"
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
