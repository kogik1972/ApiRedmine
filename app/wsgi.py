## wsgi.py
import logging
from app import create_app

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

try:
    app = create_app()
    logging.info("wsgi - ✅ Aplicación Flask creada exitosamente")
except Exception as e:
    logging.error(f"wsgi - ❌ Error al crear la aplicación Flask: {e}")
    raise
