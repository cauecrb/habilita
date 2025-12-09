from flask import render_template, request, redirect, url_for, abort
from flask_login import login_required, current_user
from . import admin_bp
from ..extensions import db
from ..models import User

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
