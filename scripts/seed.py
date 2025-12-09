import os
import secrets
from app import create_app
from app.extensions import db
from app.models import User, Profile

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
        for i in range(1, 6):
            c = create_user(f"professor{i}@habilita.local", f"Professor {i}", "professor")
            if c:
                creds.append(c)
        for i in range(1, 11):
            c = create_user(f"aluno{i}@habilita.local", f"Aluno {i}", "aluno")
            if c:
                creds.append(c)
        db.session.commit()
        instance_dir = ensure_instance_dir()
        out_path = os.path.join(instance_dir, "seed_credentials.txt")
        with open(out_path, "w", encoding="utf-8") as f:
            for email, password, role, nome in creds:
                f.write(f"{role};{nome};{email};{password}\n")

if __name__ == "__main__":
    main()
