import os
import psycopg2
from flask import current_app, g


def get_db():
    if "db" not in g:
        g.db = psycopg2.connect(
            host="postgres",
            database="misis_project",
            user=os.environ["POSTGRES_USER"],
            password=os.environ["POSTGRES_PASSWORD"],
        )

    return g.db


def close_db():
    db = g.pop("db", None)

    if db is not None:
        db.close()


def init_db():
    conn = get_db()
    cur = conn.cursor()

    with current_app.open_resource("schema.sql") as f:
        cur.execute(f.read().decode("utf8"))

    conn.commit()
