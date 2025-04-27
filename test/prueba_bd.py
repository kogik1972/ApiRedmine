import sqlite3

from utils.logging_config import configurar_logging
import logging
configurar_logging()

try:
    conn = sqlite3.connect("instance/firma.db")
    logging.info(f"prueba_bd.py - ¡Se abrió correctamente!")
    conn.close()
except Exception as e:
    logging.info(f"prueba_bd.py - Error:{e}")