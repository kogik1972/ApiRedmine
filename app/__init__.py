## app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
import logging
from dotenv import load_dotenv

db = SQLAlchemy()

def create_app():
    load_dotenv()

    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    templates_path = os.path.join(base_dir, "templates")

    app = Flask(__name__, template_folder=templates_path)

    raw_uri = os.getenv("DATABASE_URL", "sqlite:///instance/firma.db")

    if raw_uri.startswith("sqlite:///"):
        relative_path = raw_uri.replace("sqlite:///", "")
        abs_path = os.path.abspath(os.path.join(base_dir, relative_path))
        full_uri = "sqlite:///" + abs_path
    else:
        full_uri = raw_uri

    app.config['SQLALCHEMY_DATABASE_URI'] = full_uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    logging.info(f"app - Inicializando app Flask con base de datos: {full_uri}")

    db.init_app(app)
    logging.info("app - SQLAlchemy inicializado")

    from app.routes import respuestas
    app.register_blueprint(respuestas.respuestas_bp)
    logging.info("app - Blueprint 'respuestas_bp' registrado")

    return app
