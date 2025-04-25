## redmine/redmine_fields.py
import os
import requests
import logging
from dotenv import load_dotenv

load_dotenv()
modo = os.getenv("MODO_ENTORNO", "desarrollo")
if modo == "produccion":
    REDMINE_URL = os.getenv("REDMINE_URL_PROD")
else:
    REDMINE_URL = os.getenv("REDMINE_URL_DEV")

API_KEY = os.getenv("REDMINE_API_KEY")

# Cache interno
_cached_custom_fields = None

def get_json(endpoint):
    headers = {"X-Redmine-API-Key": API_KEY}
    url = f"{REDMINE_URL.rstrip('/')}/{endpoint.lstrip('/')}"
    logging.info(f"redmine_fields - 🔍 GET {url}")

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        logging.info(f"redmine_fields - ✅ Respuesta 200 OK desde {url}")
        return response.json()
    else:
        logging.error(f"redmine_fields - ❌ Error {response.status_code} al consultar {url}")
        raise Exception(f"❌ Error {response.status_code} al consultar {url}")

def get_all_custom_fields(force_reload=False):
    global _cached_custom_fields

    if _cached_custom_fields is None or force_reload:
        logging.info("redmine_fields - Consultando todos los custom_fields desde Redmine")
        data = get_json("custom_fields.json")
        _cached_custom_fields = data.get("custom_fields", [])
    else:
        logging.info("redmine_fields - Usando caché interna de custom_fields")

    return _cached_custom_fields

def get_custom_field_by_name(name, force_reload=False):
    campos = get_all_custom_fields(force_reload)
    for campo in campos:
        if campo.get("name") == name:
            logging.info(f"redmine_fields - Campo encontrado por nombre: {name}")
            return campo
    logging.warning(f"redmine_fields - No se encontró campo con nombre: {name}")
    return None

def get_custom_field_by_id(field_id, force_reload=False):
    campos = get_all_custom_fields(force_reload)
    for campo in campos:
        if campo.get("id") == field_id:
            logging.info(f"redmine_fields - Campo encontrado por ID: {field_id}")
            return campo
    logging.warning(f"redmine_fields - No se encontró campo con ID: {field_id}")
    return None
