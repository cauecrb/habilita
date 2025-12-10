from flask import render_template, request, redirect, url_for, abort
from flask_login import login_required, current_user
from . import main_bp
from ..extensions import db
from ..models import Profile, City, User, PriceTier

@main_bp.route("/")
def index():
    testimonials = [
        {"name": "Ana Souza", "city": "São Paulo", "text": "Encontrei um ótimo tutor e passei na prova prática!"},
        {"name": "Carlos Pereira", "city": "Curitiba", "text": "Aulas claras e objetivas, evoluí muito em poucas semanas."},
        {"name": "Mariana Lima", "city": "Belo Horizonte", "text": "Plataforma simples, consegui agendar e aprender no meu ritmo."},
        {"name": "João Santos", "city": "Rio de Janeiro", "text": "O professor foi paciente e as dicas fizeram toda a diferença."},
        {"name": "Fernanda Alves", "city": "Porto Alegre", "text": "Preço justo e qualidade excelente, recomendo!"},
    ]
    return render_template("index.html", testimonials=testimonials)

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
        city_id = request.form.get("city_id")
        try:
            profile.city_id = int(city_id) if city_id else None
        except ValueError:
            profile.city_id = None
        db.session.commit()
        return redirect(url_for("main.profile"))
    cities = City.query.order_by(City.nome.asc()).all()
    return render_template("profile_edit.html", profile=profile, cities=cities)

@main_bp.route("/tutors")
def tutors():
    city_id = request.args.get("city_id")
    lessons = request.args.get("lessons")
    price_min = request.args.get("price_min")
    price_max = request.args.get("price_max")
    ignore_tiers = request.args.get("ignore_tiers") in ("1", "true", "on")
    cities = City.query.order_by(City.nome.asc()).all()
    q = User.query.filter_by(role="professor")
    selected = None
    if city_id:
        try:
            cid = int(city_id)
            selected = cid
            q = q.join(Profile).filter(Profile.city_id == cid)
        except ValueError:
            pass
    tier_filters = []
    try:
        if lessons:
            l = int(lessons)
            if l > 0:
                tier_filters.append(PriceTier.lessons == l)
    except ValueError:
        pass
    try:
        if price_min:
            pmin = float(price_min)
            tier_filters.append(PriceTier.price_min >= pmin)
    except ValueError:
        pass
    try:
        if price_max:
            pmax = float(price_max)
            tier_filters.append((PriceTier.price_max == None) | (PriceTier.price_max <= pmax))
    except ValueError:
        pass
    if tier_filters and not ignore_tiers:
        from sqlalchemy import and_
        tier_subq = db.session.query(PriceTier.user_id).filter(and_(*tier_filters)).subquery()
        q = q.filter(User.id.in_(tier_subq))
    professors = q.order_by(User.created_at.desc()).all()
    return render_template(
        "tutors.html",
        cities=cities,
        professors=professors,
        selected=selected,
        selected_lessons=lessons,
        selected_price_min=price_min,
        selected_price_max=price_max,
        ignore_tiers=ignore_tiers,
    )

@main_bp.route("/pricing", methods=["GET", "POST"])
@login_required
def pricing():
    if not current_user.is_professor:
        abort(403)
    if request.method == "POST":
        action = request.form.get("action", "create")
        if action == "create":
            lessons = request.form.get("lessons")
            price_min = request.form.get("price_min")
            price_max = request.form.get("price_max")
            try:
                l = int(lessons)
                pmin = float(price_min)
                pmax = float(price_max) if price_max else None
                if l <= 0 or pmin <= 0 or (pmax is not None and pmax < pmin):
                    raise ValueError()
                tier = PriceTier(user_id=current_user.id, lessons=l, price_min=pmin, price_max=pmax)
                db.session.add(tier)
                db.session.commit()
            except Exception:
                pass
        elif action == "delete":
            tid = request.form.get("tier_id")
            try:
                t = PriceTier.query.filter_by(id=int(tid), user_id=current_user.id).first()
                if t:
                    db.session.delete(t)
                    db.session.commit()
            except Exception:
                pass
        return redirect(url_for("main.pricing"))
    tiers = PriceTier.query.filter_by(user_id=current_user.id).order_by(PriceTier.lessons.asc()).all()
    return render_template("pricing.html", tiers=tiers)
