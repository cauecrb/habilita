import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        f"sqlite:///{os.path.join(os.getcwd(), 'instance', 'habilita.db')}",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
