from flask import render_template, request, redirect, url_for, abort
from flask_login import login_required, current_user
from . import admin_bp
from ..extensions import db
from ..models import User, City, Testimonial

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

@admin_bp.route("/testimonials", methods=["GET", "POST"])
@login_required
def testimonials():
    admin_required()
    if request.method == "POST":
        action = request.form.get("action", "create")
        if action == "create":
            name = request.form.get("name", "").strip()
            city = request.form.get("city", "").strip()
            text = request.form.get("text", "").strip()
            rating = request.form.get("rating")
            try:
                rating = int(rating) if rating else None
            except ValueError:
                rating = None
            if name and text:
                db.session.add(Testimonial(name=name, city=city or None, text=text, rating=rating))
                db.session.commit()
        elif action == "delete":
            tid = request.form.get("testimonial_id")
            try:
                t = Testimonial.query.get(int(tid))
                if t:
                    db.session.delete(t)
                    db.session.commit()
            except Exception:
                pass
        elif action == "update":
            tid = request.form.get("testimonial_id")
            try:
                t = Testimonial.query.get(int(tid))
                if t:
                    t.name = request.form.get("name", t.name).strip() or t.name
                    t.city = request.form.get("city", t.city).strip() or t.city
                    t.text = request.form.get("text", t.text).strip() or t.text
                    rating = request.form.get("rating")
                    try:
                        t.rating = int(rating) if rating else None
                    except ValueError:
                        pass
                    db.session.commit()
            except Exception:
                pass
        return redirect(url_for("admin.testimonials"))
    items = Testimonial.query.order_by(Testimonial.created_at.desc()).all()
    return render_template("admin_testimonials.html", items=items)
