# redmine/redmine_client.py

import sys
import os
import requests
import logging

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from redmine.redmine_cache_sql import get_enum, get_custom_values
from utils.api import get_json
from utils.parser import parsear_enumeracion

# El dotenv ya se cargó en create_app()
REDMINE_URL = os.getenv("REDMINE_URL")
REDMINE_API_KEY = os.getenv("REDMINE_API_KEY")
if not REDMINE_URL or not REDMINE_API_KEY:
    raise RuntimeError("REDMINE_URL o REDMINE_API_KEY no están definidos")

trab_email = 'trab_email'

def obtener_emails_desde_redmine(issue_id):
    logging.info(f"redmine_client - 🔍 Consultando firmantes para issue #{issue_id}")
    try:
        issue_json = get_json(f"issues/{issue_id}.json")
        if not issue_json:
            logging.error("redmine_client - ❌ No se encontró el issue en Redmine.")
            return None

        issue_data = issue_json["issue"]
        campos_dict_issue = {campo["name"]: campo["value"] for campo in issue_data["custom_fields"]}
        id_proyecto = issue_data["project"]["id"]

        proyecto_data = get_json(f"projects/{id_proyecto}.json")["project"]
        id_proyecto_padre = proyecto_data.get("parent", {}).get("id")

        data = get_json(f"projects/{id_proyecto_padre}.json?include=custom_fields")
        campos_padre = {campo["name"]: campo["value"] for campo in data["project"]["custom_fields"]}
        email_responsable = campos_padre.get("eMail_Administrador")
        rut_responsable = campos_padre.get("RUT_Rep_Legal_Administrador")
        nombre_responsable = campos_padre.get("Nombre_Rep_Legal_Administrador")

        data = get_json(f"projects/{id_proyecto}.json?include=custom_fields")
        campos_proyecto = {campo["name"]: campo["value"] for campo in data["project"]["custom_fields"]}
        nombre_comunidad = f"RUT_{campos_proyecto.get('Comunidad')}"
        id_enum = campos_dict_issue.get(nombre_comunidad)

        if not id_enum:
            logging.error("redmine_client - ❌ No se encontró ID de enumeración.")
            return None

        enum = get_enum(id_enum)
        if not enum:
            logging.error("redmine_client - ❌ Enumeración inválida.")
            return None

        resultado = parsear_enumeracion(enum['name'])
        if not resultado:
            logging.error("redmine_client - ❌ No se pudo parsear la enumeración.")
            return None

        campos = get_custom_values(resultado['id'], "Issue")
        email_firmante = None
        for campo in campos:
            if campo['field_name'] == trab_email:
                email_firmante = campo['value']
                break

        if not email_firmante:
            logging.error("redmine_client - ❌ Email del firmante no encontrado.")
            return None

        logging.info(f"redmine_client - ✅ Firmantes recuperados correctamente para issue #{issue_id}")
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
        logging.error(f"redmine_client - ❌ Error al consultar Redmine: {e}")
        return None


# ✅ NUEVA FUNCIÓN: actualizar estado del issue
def actualizar_estado_issue(issue_id, nuevo_estado_id):
    logging.info(f"redmine_client - 🔧 Actualizando estado del issue #{issue_id} a status_id={nuevo_estado_id}")
    try:
        url = f"{REDMINE_URL}/issues/{issue_id}.json"
        headers = {
            "X-Redmine-API-Key": REDMINE_API_KEY,
            "Content-Type": "application/json"
        }
        payload = {
            "issue": {
                "status_id": nuevo_estado_id
            }
        }
        response = requests.put(url, json=payload, headers=headers)
        response.raise_for_status()
        logging.info("redmine_client - ✅ Estado actualizado correctamente.")
        return response.json()
    except requests.RequestException as e:
        logging.error(f"redmine_client - ❌ Error al actualizar el estado del issue: {e}")
        return None
