# db_init.py

import os
from flask import Flask
from db_models import db

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("SQLALCHEMY_DATABASE_URI", "sqlite:///firma.db")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    return app

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    app = create_app()

    with app.app_context():
        db.drop_all()  # ⚠️ Solo si quieres reiniciar completamente la BD
        db.create_all()
        print("✅ Base de datos inicializada correctamente.")
