## archivo_manager.py
import os
import shutil
from datetime import datetime

from utils.logging_config import configurar_logging
import logging
configurar_logging()
logger = logging.getLogger(__name__)

# Asegura que siempre se use la carpeta raíz del proyecto
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def mover_a_docs(origen, nombre_archivo):
    destino_dir = os.path.join(ROOT_DIR, 'docs')  # 👈 ahora apunta a /docs directamente
    os.makedirs(destino_dir, exist_ok=True)

    base, ext = os.path.splitext(nombre_archivo)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nuevo_nombre = f"{base}_{timestamp}{ext}"
    destino = os.path.join(destino_dir, nuevo_nombre)

    shutil.copy2(origen, destino)
    logger.info(f"archivo_manager.py - Archivo copiado a: {destino}")
    return destino, nuevo_nombre