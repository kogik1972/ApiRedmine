## redmine_cache_sql.py
## Rutina de apyo SQL a la conversion de archivos pdf al firmar
import os
import mysql.connector
from datetime import datetime

from utils.logging_config import configurar_logging
import logging
configurar_logging()

from dotenv import load_dotenv
load_dotenv()

# Directorio y archivo donde se guardará el caché
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = os.path.join(BASE_DIR, "cache")
CACHE_FILE_PATH = os.path.join(CACHE_DIR, "enumeraciones_cache.json")
CUSTOM_VALUES_CACHE_PATH = os.path.join(CACHE_DIR, "custom_values_cache.json")

def actualiza_sql(nombre_documento_docx, nombre_documento_pdf, path_documento):
    logging.info(f"convertidor_sql.py - : {path_documento} {nombre_documento_docx} {nombre_documento_pdf}")

    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

#   Modifico name, ¿description?, updated_at, 
#   Creado por Generado Automatico de Documentos EPROC
    v_fecha = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor = conn.cursor(dictionary=True)
    query = """
        update attachments set 
         filename = %s
        ,disk_filename = %s
        ,description = 'Creado y Firmado en Generador Automatico de Documentos EPROC'
        ,updated_at =  %s
        where filename = %s
        and container_type='DriveEntry';
    """
    cursor.execute(query, (nombre_documento_pdf, nombre_documento_pdf, v_fecha, nombre_documento_docx ))
    cursor.close()

#   Modifico name, ¿description?, updated_at, 
    cursor = conn.cursor(dictionary=True)
    query = """
        update drive_entries set 
         name = %s
        ,description = 'Creado y Firmado en Generador Automatico de Documentos EPROC'
        ,updated_at =  %s
        where name = %s;
    """
    cursor.execute(query, (nombre_documento_pdf, v_fecha, nombre_documento_docx ))
    cursor.close()