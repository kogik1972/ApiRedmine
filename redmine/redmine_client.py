## redmine_client.py
import sys
import os
import requests

from utils.logging_config import configurar_logging
import logging
configurar_logging()
logger = logging.getLogger(__name__)

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from redmine.redmine_cache_sql import get_enum, get_custom_values, get_firmante
from utils.api import get_json
from utils.parser import parsear_enumeracion

# El dotenv ya se cargó en create_app()
REDMINE_URL = os.getenv("REDMINE_URL")
REDMINE_API_KEY = os.getenv("REDMINE_API_KEY")
if not REDMINE_URL or not REDMINE_API_KEY:
    raise RuntimeError("REDMINE_URL o REDMINE_API_KEY no están definidos")

trab_email = 'trab_email'


def obtener_emails_desde_redmine(issue_id):
    try:
        issue_json = get_json(f"issues/{issue_id}.json")
        if not issue_json:
            logger.info("redmine_client.py - No se encontró el issue en Redmine.")
            return None

        issue_data = issue_json["issue"]
        campos_dict_issue = {campo["name"]: campo["value"] for campo in issue_data["custom_fields"]}
        id_proyecto = issue_data["project"]["id"]

        # OBTENGO INFORMACION TRABAJADOR FIRMA
        data = get_json(f"projects/{id_proyecto}.json?include=custom_fields")
        campos_proyecto = {campo["name"]: campo["value"] for campo in data["project"]["custom_fields"]}
        nombre_comunidad = f"RUT_{campos_proyecto.get('Comunidad')}"
        id_enum = campos_dict_issue.get(nombre_comunidad)
        if not id_enum:
            logger.info("redmine_client.py - No se encontró ID de enumeración.")
            return None
        enum = get_enum(id_enum)
        if not enum:
            logger.info("redmine_client.py - Enumeración inválida.")
            return None

        resultado = parsear_enumeracion(enum['name'])
        if not resultado:
            logger.info("redmine_client.py - No se pudo parsear la enumeración.")
            return None

        campos = get_custom_values(resultado['id'], "Issue")
        email_firmante = None
        for campo in campos:
            if campo['field_name'] == trab_email:
                email_firmante = campo['value']
                break

        if not email_firmante:
            logger.info("redmine_client.py - Email del firmante no encontrado.")
            return None

        # OBTENGO INFORMACION RESPONSABLE FIRMA
        email_responsable = None
        rut_responsable = None
        nombre_responsable = None
        campos = get_firmante(resultado['id'])
        for campo in campos:
            email_responsable = campo.get('email_responsable')
            rut_responsable = campo.get('rut_responsable')
            nombre_responsable = campo.get('nombre_responsable')

        logger.info(f"redmine_client.py - email_responsable: {email_responsable}")
        logger.info(f"redmine_client.py - rut_responsable: {rut_responsable}")
        logger.info(f"redmine_client.py - nombre_responsable: {nombre_responsable}")

        if not email_responsable or not rut_responsable or not nombre_responsable:
            logger.info(f"redmine_client.py - email_responsable: {email_responsable} no encontrado.")
            logger.info(f"redmine_client.py - rut_responsable: {rut_responsable} no encontrado.")
            logger.info(f"redmine_client.py - nombre_responsable: {nombre_responsable} no encontrado.")
            return None

        return {
            "responsable": {
                "nombre": nombre_responsable,
                "rut": rut_responsable,
                "email": email_responsable
            },
            "firmante": {
                "nombre": resultado['nombre'],
                "rut": resultado['rut'],
                "email": email_firmante
            }
        }

    except requests.RequestException as e:
        logger.info(f"redmine_client.py - Error al consultar Redmine: {e}")
        return None


def actualizar_estado_issue(issue_id, status_id):
    try:
        url = f"{REDMINE_URL}/issues/{issue_id}.json"

        logger.info(f"redmine_client.py - URL: {url} - {issue_id} - {status_id}")
        logger.info(f"redmine_client.py - REDMINE_API_KEY: {REDMINE_API_KEY}")

        headers = {
            "X-Redmine-API-Key": REDMINE_API_KEY,
            "Content-Type": "application/json"
        }
        payload = {
            "issue": {
                "status_id": status_id
            }
        }

        response = requests.put(url, json=payload, headers=headers)

        if response.status_code == 200:
            logger.info(f"redmine_client.py - Issue {issue_id} actualizado correctamente a status_id={status_id}")
            return True
        else:
            logger.info(f"redmine_client.py - Error al actualizar issue {issue_id}: {response.status_code} - {response.text}")
            return False

    except Exception as e:
        logger.info(f"redmine_client.py - Excepción al actualizar issue {issue_id}: {e}")
        return False