## __init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv

db = SQLAlchemy()

def create_app():
    load_dotenv()

    # Base absoluta del proyecto
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    templates_path = os.path.join(base_dir, "templates")

    # Inicializa Flask con ruta explícita de templates
    #app = Flask(__name__, template_folder=templates_path)
    static_path = os.path.join(base_dir, "static")
    app = Flask(__name__, template_folder=templates_path, static_folder=static_path)

    # Obtener URI desde el .env
    raw_uri = os.getenv("DATABASE_URL", "sqlite:///instance/firma.db")

    # Convertir a ruta absoluta si es SQLite
    if raw_uri.startswith("sqlite:///"):
        relative_path = raw_uri.replace("sqlite:///", "")
        abs_path = os.path.abspath(os.path.join(base_dir, relative_path))
        full_uri = "sqlite:///" + abs_path
    else:
        full_uri = raw_uri

    app.config['SQLALCHEMY_DATABASE_URI'] = full_uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    # 👇 Registro de blueprints
    from app.routes import responder
    from app.routes.validar import validar_bp

    app.register_blueprint(responder.respuestas_bp)
    app.register_blueprint(validar_bp)

    return app
