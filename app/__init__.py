from flask import Flask
from dotenv import load_dotenv
import os

from db import db  # o como sea que inicialices SQLAlchemy

load_dotenv()

def create_app():
    app = Flask(__name__)

    # Configuración
    app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Inicializar extensiones
    db.init_app(app)

    # 👉 Registrar rutas (aquí va lo nuestro)
    from app.routes.respuestas import respuestas_bp
    app.register_blueprint(respuestas_bp)

    return app
