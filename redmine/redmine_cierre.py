## redmine_cierre.py
from redmine.redmine_client import actualizar_estado_issue

from utils.logging_config import configurar_logging
import logging
configurar_logging()
logger = logging.getLogger(__name__)

def cerrar_issue_firma(issue_id, estado):
    try:
        logger.info(f"redmine_cierre.py - Iniciando cierre de issue {issue_id} con estado {estado}")

        # Mapeo interno de estado a status_id de Redmine
        if estado == "firmado":
            status_id = 14  # Los firmantes han aceptado firmar el respectivo documento
        elif estado == "rechazado":
            status_id = 15  # Uno o Todos los firmantes han rechazado firmar el respectivo documento
        else:
            logger.error(f"redmine_cierre.py - Estado desconocido: {estado}")
            return False

        actualizar_estado_issue(issue_id, status_id)
        logger.info(f"redmine_cierre.py - Issue {issue_id} actualizado correctamente a estado {estado}")
        return True

    except Exception as e:
        logger.error(f"redmine_cierre.py - Error cerrando issue {issue_id}: {e}", exc_info=True)
        return False