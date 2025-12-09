from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user
from . import auth_bp
from ..extensions import db
from ..models import User, Profile

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for("main.index"))
        flash("Credenciais inválidas.")
    return render_template("login.html")

@auth_bp.route("/logout")
def logout():
    if current_user.is_authenticated:
        logout_user()
    return redirect(url_for("main.index"))

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        role = request.form.get("role", "aluno")

        if not email or not password:
            flash("Preencha email e senha.")
            return render_template("register.html")

        if User.query.filter_by(email=email).first():
            flash("Email já cadastrado.")
            return render_template("register.html")

        if User.query.count() == 0:
            role = "administrador"
        else:
            if role not in {"professor", "aluno"}:
                role = "aluno"

        user = User(email=email, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.flush()
        profile = Profile(user_id=user.id, nome=nome)
        db.session.add(profile)
        db.session.commit()
        login_user(user)
        return redirect(url_for("main.edit_profile"))

    return render_template("register.html")
