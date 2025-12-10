import os
import secrets
from app import create_app
from app.extensions import db
from app.models import User, Profile, City, PriceTier

def ensure_instance_dir():
    path = os.path.join(os.getcwd(), "instance")
    os.makedirs(path, exist_ok=True)
    return path

def create_user(email, nome, role):
    existing = User.query.filter_by(email=email).first()
    if existing:
        return None
    password = secrets.token_urlsafe(10)
    user = User(email=email, role=role)
    user.set_password(password)
    db.session.add(user)
    db.session.flush()
    profile = Profile(user_id=user.id, nome=nome)
    db.session.add(profile)
    return (email, password, role, nome)

def main():
    app = create_app()
    with app.app_context():
        creds = []
        if City.query.count() == 0:
            cities_data = [
                ("São Paulo", "SP"),
                ("Rio de Janeiro", "RJ"),
                ("Belo Horizonte", "MG"),
                ("Curitiba", "PR"),
                ("Porto Alegre", "RS"),
            ]
            for nome, uf in cities_data:
                db.session.add(City(nome=nome, uf=uf))
            db.session.commit()
        cities = City.query.all()
        for i in range(1, 6):
            c = create_user(f"professor{i}@habilita.local", f"Professor {i}", "professor")
            if c:
                creds.append(c)
        for i in range(1, 11):
            c = create_user(f"aluno{i}@habilita.local", f"Aluno {i}", "aluno")
            if c:
                creds.append(c)
        db.session.flush()
        # atribui cidade aleatória aos perfis criados nesta execução
        import random
        for email, _, _, _ in creds:
            u = User.query.filter_by(email=email).first()
            if u and u.profile and cities:
                u.profile.city_id = random.choice(cities).id
                if u.is_professor:
                    for lessons, pmin, pmax in [(5, 300, 500), (10, 550, 900)]:
                        if not PriceTier.query.filter_by(user_id=u.id, lessons=lessons).first():
                            db.session.add(PriceTier(user_id=u.id, lessons=lessons, price_min=pmin, price_max=pmax))
        db.session.commit()
        instance_dir = ensure_instance_dir()
        out_path = os.path.join(instance_dir, "seed_credentials.txt")
        with open(out_path, "w", encoding="utf-8") as f:
            for email, password, role, nome in creds:
                f.write(f"{role};{nome};{email};{password}\n")

if __name__ == "__main__":
    main()
