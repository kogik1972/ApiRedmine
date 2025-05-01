## db_init
import os
import sys
sys.path.append(os.path.abspath(os.path.dirname(__file__) + "/.."))  # para encontrar `app`

from utils.logging_config import configurar_logging
import logging
configurar_logging()
logger = logging.getLogger(__name__)

from app import create_app, db
app = create_app()

with app.app_context():
    logger.info(f"Eliminando base si existe...")
    db.drop_all()
    logger.info(f"Creando base desde cero...")
    db.create_all()
    logger.info(f"Base de datos lista en: {app.config['SQLALCHEMY_DATABASE_URI']}")
