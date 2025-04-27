import os
import sys
sys.path.append(os.path.abspath(os.path.dirname(__file__) + "/.."))  # para encontrar `app`

from utils.logging_config import configurar_logging
import logging
configurar_logging()

from app import create_app, db
app = create_app()

with app.app_context():
    logging.info(f"db_init.py - Eliminando base si existe...")
    db.drop_all()
    logging.info(f"db_init.py - Creando base desde cero...")
    db.create_all()
    logging.info(f"db_init.py - Base de datos lista en: {app.config['SQLALCHEMY_DATABASE_URI']}")
