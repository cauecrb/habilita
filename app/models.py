from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from .extensions import db, login_manager

class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(255), unique=True, nullable=False)
    uf = db.Column(db.String(2))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(32), nullable=False, default="aluno")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    profile = db.relationship("Profile", backref="user", uselist=False, cascade="all, delete-orphan")
    price_tiers = db.relationship("PriceTier", backref="user", cascade="all, delete-orphan")

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self) -> bool:
        return self.role == "administrador"

    @property
    def is_professor(self) -> bool:
        return self.role == "professor"

    @property
    def is_aluno(self) -> bool:
        return self.role == "aluno"

class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    nome = db.Column(db.String(255))
    telefone = db.Column(db.String(64))
    bio = db.Column(db.Text)
    city_id = db.Column(db.Integer, db.ForeignKey("city.id"))
    city = db.relationship("City")

class PriceTier(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    lessons = db.Column(db.Integer, nullable=False)
    price_min = db.Column(db.Numeric(10, 2), nullable=False)
    price_max = db.Column(db.Numeric(10, 2))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
