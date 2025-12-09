from flask import render_template, request, redirect, url_for, abort
from flask_login import login_required, current_user
from . import main_bp
from ..extensions import db
from ..models import Profile

@main_bp.route("/")
def index():
    return render_template("index.html")

@main_bp.route("/profile")
@login_required
def profile():
    profile = current_user.profile
    return render_template("profile.html", profile=profile)

@main_bp.route("/profile/edit", methods=["GET", "POST"])
@login_required
def edit_profile():
    profile = current_user.profile
    if request.method == "POST":
        profile.nome = request.form.get("nome", "").strip()
        profile.telefone = request.form.get("telefone", "").strip()
        profile.bio = request.form.get("bio", "").strip()
        db.session.commit()
        return redirect(url_for("main.profile"))
    return render_template("profile_edit.html", profile=profile)
