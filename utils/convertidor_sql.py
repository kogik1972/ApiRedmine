## convertidor_sql.py
## Rutina de apoyo SQL a la conversión de archivos PDF al firmar

import os
import mysql.connector
from datetime import datetime

from utils.logging_config import configurar_logging
import logging
configurar_logging()
logger = logging.getLogger(__name__)

from dotenv import load_dotenv
load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = os.path.join(BASE_DIR, "cache")
CACHE_FILE_PATH = os.path.join(CACHE_DIR, "enumeraciones_cache.json")
CUSTOM_VALUES_CACHE_PATH = os.path.join(CACHE_DIR, "custom_values_cache.json")

def actualiza_sql(nombre_documento_docx, nombre_documento_pdf, path_documento):
    logger.info(f"convertidor_sql.py - : {path_documento} {nombre_documento_docx} {nombre_documento_pdf}")

    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

    v_fecha = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Actualiza la tabla attachments
    cursor = conn.cursor(dictionary=True)
    query = """
        UPDATE attachments SET 
            filename = %s,
            disk_filename = %s,
            description = 'Creado y Firmado en Generador Automatico de Documentos EPROC'
        WHERE filename = %s
          AND container_type = 'DriveEntry';
    """
    cursor.execute(query, (nombre_documento_pdf, nombre_documento_pdf, nombre_documento_docx))
    conn.commit()  # ✅ commit explícito
    cursor.close()

    # Actualiza la tabla drive_entries
    cursor = conn.cursor(dictionary=True)
    query = """
        UPDATE drive_entries SET 
            name = %s,
            description = 'Creado y Firmado en Generador Automatico de Documentos EPROC',
            updated_at = %s
        WHERE name = %s;
    """
    cursor.execute(query, (nombre_documento_pdf, v_fecha, nombre_documento_docx))
    conn.commit()  # ✅ commit explícito
    cursor.close()

    conn.close()
    return "200"
