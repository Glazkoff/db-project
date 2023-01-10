from flask import (
    render_template,
    redirect,
)
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from app import app
from .db import get_db, close_db

# Авторизация

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[InputRequired(), Length(max=255)])
    password = PasswordField("Пароль", validators=[InputRequired()])
    submit = SubmitField("Войти")


class User(UserMixin):
    def __init__(
        self,
        user_id,
        name,
        email,
        password,
    ):
        self.id = user_id
        self.name = name
        self.email = email
        self.password = password


# Загружаем пользователя из БД
@login_manager.user_loader
def load_user(user_id):
    conn = get_db()
    cur = conn.cursor()
    query = "SELECT * FROM users WHERE id = %s"
    cur.execute(query, (user_id,))
    user = cur.fetchone()
    close_db()
    return User(*user) if user is not None else None


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        conn = get_db()
        cur = conn.cursor()
        query = "SELECT * FROM users WHERE email = %s AND password = %s"
        cur.execute(query, (form.email.data, form.password.data))
        user = cur.fetchone()
        close_db()

        if user is None:
            return render_template(
                "login.html", form=form, error="Некорректные логин или пароль"
            )
        user_obj = User(*user)
        login_user(user_obj)
        return redirect("/")
    return render_template("login.html", form=form)


@app.route("/protected")
@login_required
def protected():
    return "Вы авторизованы!"


@app.route("/logout")
def logout():
    logout_user()
    return render_template(
        "success_logout.html",
    )
