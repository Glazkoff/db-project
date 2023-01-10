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

ingredients_blueprint = Blueprint("ingredients", __name__)

# CREATE API
@ingredients_blueprint.post(f"{API_PREFIX}/admin/ingredients")
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
        return redirect("/admin?tab=ingredients")
    else:
        abort(500)


# UPDATE API
@ingredients_blueprint.put(f"{API_PREFIX}/ingredients/<int:id>")
@login_required
def update_ingredient(id):
    conn = get_db()
    cur = conn.cursor()
    req = "UPDATE ingredients SET ingredient_name = %s WHERE id = (%s)"
    ingredient_name = request.form.get("ingredient_name", "")
    cur.execute(
        req,
        (
            ingredient_name,
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
@ingredients_blueprint.delete(f"{API_PREFIX}/ingredients/<int:id>")
@login_required
def delete_ingredient(id):
    conn = get_db()
    cur = conn.cursor()
    req = "DELETE FROM ingredients WHERE id = (%s)"
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
