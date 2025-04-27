import os
import requests
from dotenv import load_dotenv
load_dotenv()

from utils.logging_config import configurar_logging
import logging
configurar_logging()

modo = os.getenv("MODO_ENTORNO", "desarrollo")
if modo == "produccion":
    REDMINE_URL = os.getenv("REDMINE_URL_PROD")
else:
    REDMINE_URL = os.getenv("REDMINE_URL_DEV")

API_KEY = os.getenv("REDMINE_API_KEY")

# Cache interno para evitar múltiples llamadas a Redmine
_cached_custom_fields = None

def get_json(endpoint):
    """Realiza una solicitud GET a la API REST de Redmine."""
    headers = {
        "X-Redmine-API-Key": API_KEY
    }
    url = f"{REDMINE_URL.rstrip('/')}/{endpoint.lstrip('/')}"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"❌ Error {response.status_code} al consultar {url}")


def get_all_custom_fields(force_reload=False):
    """Obtiene todos los custom_fields desde Redmine (usa caché por defecto)."""
    global _cached_custom_fields

    if _cached_custom_fields is None or force_reload:
        data = get_json("custom_fields.json")
        _cached_custom_fields = data.get("custom_fields", [])

    return _cached_custom_fields


def get_custom_field_by_name(name, force_reload=False):
    """Devuelve el diccionario completo de un custom_field por su nombre."""
    campos = get_all_custom_fields(force_reload)
    for campo in campos:
        if campo.get("name") == name:
            return campo
    return None


def get_custom_field_by_id(field_id, force_reload=False):
    """Devuelve el custom_field por su ID numérico."""
    campos = get_all_custom_fields(force_reload)
    for campo in campos:
        if campo.get("id") == field_id:
            return campo
    return None
