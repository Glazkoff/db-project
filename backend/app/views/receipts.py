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
from wtforms.validators import DataRequired, NumberRange
from ..db import get_db, close_db
from .general import API_PREFIX

receipts_blueprint = Blueprint("receipts", __name__)


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


def get_ingredients():
    ingredients = []
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT id, ingredient_name FROM ingredients")
        rows = cur.fetchall()
        for row in rows:
            ingredients.append((row[0], row[1]))
    except Exception as e:
        raise ValidationError(str(e))
    finally:
        close_db()
    return ingredients


def get_units():
    units = []
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT id, short_name FROM units")
        rows = cur.fetchall()
        for row in rows:
            units.append((row[0], row[1]))
    except Exception as e:
        raise ValidationError(str(e))
    finally:
        close_db()
    return units


# CREATE VIEW
@receipts_blueprint.route("/add_receipt")
@login_required
def add_receipt_view():

    units = get_units()
    ingredients = get_ingredients()

    class IngredientForm(FlaskForm):
        ingredient = SelectField("Название", coerce=int, choices=ingredients)
        unit = SelectField("Ед.измерения", coerce=int, choices=units)
        amount = IntegerField("Количество", validators=[NumberRange(min=1)])
        comment = StringField("Комментарий")

    class NewIngredientForm(FlaskForm):
        ingredient_name = StringField("Название", validators=[DataRequired()])
        unit = SelectField("Ед.измерения", validators=[DataRequired()], choices=units)
        amount = IntegerField(
            "Количество", validators=[NumberRange(min=1), DataRequired()]
        )
        comment = StringField("Комментарий")

    class AddReceiptForm(FlaskForm):
        title = StringField("Название", validators=[DataRequired()])
        body = TextAreaField("Текст рецепта", validators=[DataRequired()])
        category = SelectField("Категории", coerce=int, choices=get_categories())
        ingredients = FieldList(FormField(IngredientForm))
        new_ingredients = FieldList(FormField(NewIngredientForm))

    form = AddReceiptForm()
    return render_template(
        "add_receipt.html", form=form, units=units, ingredients=ingredients
    )


# CREATE API
@receipts_blueprint.post(f"{API_PREFIX}/add_receipt")
@login_required
def add_receipt():
    conn = get_db()
    cur = conn.cursor()

    title = request.form["title"]
    body = request.form["body"]
    category_id = request.form["category"]
    author_id = current_user.id
    ingredients = request.form.getlist("ingredient")
    units = request.form.getlist("unit")
    amounts = request.form.getlist("amount")
    comments = request.form.getlist("comment")
    new_ingredient_names = request.form.getlist("new_ingredient_name")
    new_ingredient_units = request.form.getlist("new_ingredient_unit")
    new_ingredient_amounts = request.form.getlist("new_ingredient_amount")
    new_ingredient_comments = request.form.getlist("new_ingredient_comment")

    try:
        cur.execute(
            "INSERT INTO receipts (title, body, category_id, author_id) VALUES (%s, %s, %s, %s) RETURNING id",
            (title, body, category_id, author_id),
        )
        receipt_id = cur.fetchone()[0]

        # связь с существующими ингредиентами
        for i in range(len(ingredients)):
            cur.execute(
                "INSERT INTO ingredients_in_receipts (ingredient_id, receipt_id, unit_id, amount, comment) VALUES (%s, %s, %s, %s, %s)",
                (ingredients[i], receipt_id, units[i], amounts[i], comments[i]),
            )

        # добавление новых ингредиентов
        for i in range(len(new_ingredient_names)):
            cur.execute(
                "INSERT INTO ingredients (ingredient_name) VALUES (%s) RETURNING id",
                (new_ingredient_names[i],),
            )
            new_ingredient_id = cur.fetchone()[0]
            cur.execute(
                "INSERT INTO ingredients_in_receipts (ingredient_id, receipt_id, unit_id, amount, comment) VALUES (%s, %s, %s, %s, %s)",
                (
                    new_ingredient_id,
                    receipt_id,
                    new_ingredient_units[i],
                    new_ingredient_amounts[i],
                    new_ingredient_comments[i],
                ),
            )
        conn.commit()
    except Exception as e:
        raise ValidationError(str(e))
    finally:
        close_db()
    return redirect(f"/receipts/{receipt_id}")


# RETRIEVE VIEW
@receipts_blueprint.route("/receipts/<int:id>")
def receipt_detalization_view(id):
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    receipt_req = "SELECT * FROM receipts WHERE id = (%s)"
    cur.execute(receipt_req, (id,))
    receipt = cur.fetchone()
    categories_hierarchy_req = """
        WITH RECURSIVE category_chain (id, category_name, parent_category_id, level) AS (
            SELECT id,
                category_name,
                parent_category_id,
                1 as level
            FROM categories
            WHERE id = (SELECT category_id FROM receipts WHERE id = %s)
            UNION ALL
            SELECT c.id,
                c.category_name,
                c.parent_category_id,
                cc.level + 1 as level
            FROM categories c
                JOIN category_chain cc ON cc.parent_category_id = c.id
            )
        SELECT *
        FROM category_chain ORDER BY level DESC;
    """
    cur.execute(categories_hierarchy_req, (id,))
    categories_hierarchy = cur.fetchall()
    cur.execute(
        """
            SELECT r.*, u.name, u.email FROM receipts r
            RIGHT JOIN users u ON r.author_id = u.id
            WHERE r.id = %s;
            """,
        (id,),
    )
    result = cur.fetchone()
    print("result", result)
    receipt = {
        "id": result["id"],
        "title": result["title"],
        "body": result["body"],
        "updated_at": result["updated_at"],
        "created_at": result["created_at"],
    }
    author = {"name": result["name"], "email": result["email"]}

    cur.execute(
        """
            SELECT iir.*, i.ingredient_name, u.short_name
            FROM ingredients_in_receipts iir, ingredients i, units u
            WHERE iir.ingredient_id = i.id
            AND iir.unit_id = u.id
            AND iir.receipt_id = %s;
        """,
        (id,),
    )
    ingredients = cur.fetchall()
    close_db()
    return render_template(
        "receipt.html",
        receipt=receipt,
        categories=categories_hierarchy,
        ingredients=ingredients,
        author=author,
    )


# UPDATE VIEW
@receipts_blueprint.route("/receipts/update/<int:id>")
@login_required
def receipt_update_view(id):
    class EditReceiptForm(FlaskForm):
        title = StringField("Название", validators=[DataRequired()])
        body = TextAreaField("Текст рецепта", validators=[DataRequired()])
        category = SelectField("Категории", coerce=int, choices=get_categories())
        ingredients = []

    form = EditReceiptForm()

    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            "SELECT title, body, category_id, id FROM receipts WHERE id=%s", (id,)
        )
        receipt = cur.fetchone()
        form.title.data = receipt[0]
        form.body.data = receipt[1]
        form.category.data = receipt[2]

        cur.execute(
            "SELECT ingredient_id, unit_id, amount, comment FROM ingredients_in_receipts WHERE receipt_id=%s",
            (id,),
        )
        ingredients_data = cur.fetchall()
        form.ingredients = [
            {
                "ingredient_id": ingredient[0],
                "unit_id": ingredient[1],
                "amount": ingredient[2],
                "comment": ingredient[3],
            }
            for ingredient in ingredients_data
        ]
    except Exception as e:
        raise e
    finally:
        close_db()

    return render_template(
        "update_receipt.html",
        form=form,
        ingredients=get_ingredients(),
        units=get_units(),
        receipt=receipt,
    )


# UPDATE API
@receipts_blueprint.put(f"{API_PREFIX}/receipts/<int:id>")
@login_required
def update_receipt(id):
    conn = get_db()
    cur = conn.cursor()
    title = request.form["title"]
    body = request.form["body"]
    category = request.form["category"]
    ingredients = request.form.getlist("ingredient_id")
    units = request.form.getlist("unit_id")
    amounts = request.form.getlist("amount")
    comments = request.form.getlist("comment")

    try:
        cur.execute(
            "UPDATE receipts SET title=%s, body=%s, category_id=%s WHERE id=%s",
            (title, body, category, id),
        )
        cur.execute("DELETE FROM ingredients_in_receipts WHERE receipt_id=%s", (id,))
        for i in range(len(ingredients)):
            cur.execute(
                "INSERT INTO ingredients_in_receipts (ingredient_id, receipt_id, unit_id, amount, comment) VALUES (%s, %s, %s, %s, %s)",
                (ingredients[i], id, units[i], amounts[i], comments[i]),
            )
        conn.commit()
    except Exception as e:
        raise e
    finally:
        close_db()
    return make_response(
        jsonify({"message": "Успешно обновлено", "success": True}), 200
    )


# DELETE API
@receipts_blueprint.delete(f"{API_PREFIX}/receipts/<int:id>")
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
