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


def build_category_tree(parent_id=None):
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    if parent_id:
        cur.execute(
            "SELECT c.*, (SELECT COUNT(r.id) FROM receipts as r WHERE r.category_id = c.id) as count_receipts FROM categories as c WHERE c.parent_category_id = %s",
            (parent_id,),
        )
    else:
        cur.execute(
            "SELECT c.*, (SELECT COUNT(r.id) FROM receipts as r WHERE r.category_id = c.id) as count_receipts FROM categories as c WHERE c.parent_category_id is null"
        )
    rows = cur.fetchall()
    categories = {}
    for row in rows:
        id = row["id"]
        name = row["category_name"]
        count_receipts = row["count_receipts"]
        categories[id] = {
            "name": name,
            "count_receipts": count_receipts,
            "children": build_category_tree(id),
        }
    return categories


# RETRIEVE VIEW
@categories_blueprint.route("/categories/<int:id>")
def receipts_by_category(id):
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT * FROM categories WHERE id = '%s'", (id,))
    category = cur.fetchone()
    receipts_req = """
        WITH RECURSIVE sub_categories(id, category_name, parent_category_id) AS (
            SELECT id, category_name, parent_category_id
            FROM categories
            WHERE id = %s
            UNION
            SELECT c.id, c.category_name, c.parent_category_id
            FROM sub_categories as sc
            JOIN categories as c ON sc.id = c.parent_category_id
        )
        SELECT r.id, r.title, r.created_at, r.updated_at, u.name as author_name, c.category_name, c.id as category_id FROM receipts as r 
        INNER JOIN sub_categories as c ON r.category_id = c.id
        INNER JOIN users as u ON r.author_id = u.id;
    """
    cur.execute(receipts_req, (id,))
    receipts = cur.fetchall()
    close_db()
    return render_template(
        "category_receipts.html", category=category, receipts=receipts
    )


# READ LIST VIEW
@categories_blueprint.route("/categories")
def categories():
    category_tree = build_category_tree()
    return render_template("categories.html", category_tree=category_tree)


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
