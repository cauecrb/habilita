from flask import render_template, request, redirect, url_for, abort
from flask_login import login_required, current_user
from . import admin_bp
from ..extensions import db
from ..models import User, City

def admin_required():
    if not current_user.is_authenticated or current_user.role != "administrador":
        abort(403)

@admin_bp.route("/users", methods=["GET", "POST"])
@login_required
def users():
    admin_required()
    if request.method == "POST":
        user_id = int(request.form.get("user_id"))
        role = request.form.get("role", "aluno")
        if role not in {"administrador", "professor", "aluno"}:
            role = "aluno"
        user = User.query.get_or_404(user_id)
        user.role = role
        db.session.commit()
        return redirect(url_for("admin.users"))
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template("admin_users.html", users=users)

@admin_bp.route("/cities", methods=["GET", "POST"])
@login_required
def cities():
    admin_required()
    if request.method == "POST":
        action = request.form.get("action", "create")
        if action == "create":
            nome = request.form.get("nome", "").strip()
            uf = request.form.get("uf", "").strip().upper()[:2] or None
            if nome:
                if not City.query.filter_by(nome=nome).first():
                    c = City(nome=nome, uf=uf)
                    db.session.add(c)
                    db.session.commit()
        elif action == "delete":
            cid = request.form.get("city_id")
            try:
                c = City.query.get(int(cid))
                if c:
                    db.session.delete(c)
                    db.session.commit()
            except Exception:
                pass
        return redirect(url_for("admin.cities"))
    cities = City.query.order_by(City.nome.asc()).all()
    return render_template("admin_cities.html", cities=cities)
