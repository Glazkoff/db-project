from flask import render_template, redirect, request
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
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

    def set_password(self, password):
        print(
            "generate_password_hash(password)",
            password,
            generate_password_hash(password),
        )
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


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
    if request.method == "POST":
        conn = get_db()
        cur = conn.cursor()
        email = request.form["email"]
        password = request.form["password"]
        remember_me = request.form.get("remember_me")
        cur.execute(
            "SELECT id, name, email, password FROM users WHERE email = %s", (email,)
        )
        user_data = cur.fetchone()
        print("user_data", user_data)
        if user_data:
            user = User(*user_data)
            if user.check_password(password):
                login_user(user, remember=remember_me)
                return redirect("/")
            else:
                return render_template(
                    "login.html", error="Неправильный логин или пароль"
                )
        else:
            return render_template("login.html", error="Неправильный логин или пароль")
    return render_template("login.html")


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


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        conn = get_db()
        cur = conn.cursor()
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        user = User(None, name, email, password)
        user.set_password(password)
        cur.execute(
            "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
            (user.name, user.email, user.password),
        )
        print(
            "user.name, user.email, user.password", user.name, user.email, user.password
        )
        conn.commit()
        close_db()
        return redirect("/login")
    return render_template("register.html")
