import psycopg2.extras
from flask import render_template, jsonify, make_response, abort, request, redirect
from flask_login import login_required, current_user
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
        current_user=current_user,
    )


@app.route("/receipt/<int:id>")
def receipt_detalization_view(id):
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    req = "SELECT * FROM receipts WHERE id = (%s)"
    cur.execute(req, (id,))
    receipt = cur.fetchone()
    close_db()
    return render_template("receipt.html", receipt=receipt)


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
    return render_template("add_receipt.html")


@app.post(f"{API_PREFIX}/add_receipt")
@login_required
def add_receipt():
    conn = get_db()
    cur = conn.cursor()
    title = request.form.get("title", "")
    body = request.form.get("body", "")
    cur.execute(
        "INSERT INTO receipts (title, body) VALUES (%s, %s) RETURNING id",
        (title, body),
    )
    rows_affected = cur.rowcount
    conn.commit()
    close_db()
    if rows_affected > 0:
        return redirect("/")
    else:
        abort(500)


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
    dashboard_data = {}
    average_ingredients_count_req = """
        SELECT AVG(num_ingredients) AS avg_ingredients 
        FROM (SELECT COUNT(ingredients_in_receipts.id) AS num_ingredients 
        FROM ingredients_in_receipts 
        GROUP BY ingredients_in_receipts.receipt_id) 
        AS ingredients_count;
    """
    conn = get_db()
    cur = conn.cursor()
    cur.execute(average_ingredients_count_req)
    dashboard_data["average_ingredients_count"] = cur.fetchone()
    close_db()
    return render_template("admin.html", dashboard_data=dashboard_data)
