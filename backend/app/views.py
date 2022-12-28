import psycopg2.extras
from flask import render_template, jsonify, make_response, abort, request, redirect
from app import app
from .db import get_db

API_PREFIX = "/api"


@app.route("/")
def home_template():
    conn = get_db()
    cur = conn.cursor()
    req = "SELECT * FROM receipts ORDER BY id DESC LIMIT 10"
    cur.execute(req)
    receipts = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("home.html", receipts=receipts)


@app.route("/receipt/<int:id>")
def receipt_detalization_view(id):
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    req = "SELECT * FROM receipts WHERE id = (%s)"
    cur.execute(req, (id,))
    receipt = cur.fetchone()
    cur.close()
    conn.close()
    return render_template("receipt.html", receipt=receipt)


@app.route("/receipt/update/<int:id>")
def receipt_update_view(id):
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    req = "SELECT * FROM receipts WHERE id = (%s)"
    cur.execute(req, (id,))
    receipt = cur.fetchone()
    cur.close()
    conn.close()
    return render_template("update_receipt.html", receipt=receipt)


@app.put(f"{API_PREFIX}/receipt/<int:id>")
def update_receipt(id):
    print("!!!!")
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
    cur.close()
    conn.close()
    if rows_updated > 0:
        return make_response(
            jsonify({"message": "Успешно обновлено", "success": True}), 200
        )
    else:
        return make_response(
            jsonify({"message": "Произошла ошибка", "success": False}), 400
        )


@app.delete(f"{API_PREFIX}/receipt/<int:id>")
def delete_receipt(id):
    conn = get_db()
    cur = conn.cursor()
    req = "DELETE FROM receipts WHERE id = (%s)"
    cur.execute(req, (id,))
    rows_deleted = cur.rowcount
    conn.commit()
    cur.close()
    conn.close()
    if rows_deleted > 0:
        return make_response(
            jsonify({"message": "Успешно удалено", "success": True}), 200
        )
    else:
        return make_response(
            jsonify({"message": "Произошла ошибка", "success": False}), 400
        )


@app.route("/add_receipt")
def add_receipt_view():
    return render_template("add_receipt.html")


@app.post(f"{API_PREFIX}/add_receipt")
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
    cur.close()
    conn.close()
    if rows_affected > 0:
        return redirect("/")
    else:
        abort(500)


@app.route("/test")
def hello_world():
    return jsonify(hello="world")


@app.route("/error")
def error_view():
    return render_template("error.html")


@app.route("/success")
def success_view():
    return render_template("success.html")
