from flask import (
    jsonify,
    make_response,
    abort,
    request,
    redirect,
    Blueprint,
)
from flask_login import login_required, current_user
from ..db import get_db, close_db
from .general import API_PREFIX

units_blueprint = Blueprint("units", __name__)

# CREATE API
@units_blueprint.post(f"{API_PREFIX}/units")
@login_required
def add_unit():
    conn = get_db()
    cur = conn.cursor()
    short_name = request.form.get("short_name", "")
    full_name = request.form.get("full_name", "")
    cur.execute(
        "INSERT INTO units (short_name, full_name) VALUES (%s, %s) RETURNING id",
        (
            short_name,
            full_name,
        ),
    )
    rows_affected = cur.rowcount
    conn.commit()
    close_db()
    if rows_affected > 0:
        return redirect("/admin?tab=units")
    else:
        abort(500)


# UPDATE API
@units_blueprint.put(f"{API_PREFIX}/units/<int:id>")
@login_required
def update_unit(id):
    conn = get_db()
    cur = conn.cursor()
    req = "UPDATE units SET short_name = %s, full_name = %s WHERE id = (%s)"
    short_name = request.form.get("short_name", "")
    full_name = request.form.get("full_name", "")
    cur.execute(
        req,
        (
            short_name,
            full_name,
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
@units_blueprint.delete(f"{API_PREFIX}/units/<int:id>")
@login_required
def delete_unit(id):
    conn = get_db()
    cur = conn.cursor()
    req = "DELETE FROM units WHERE id = (%s)"
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
