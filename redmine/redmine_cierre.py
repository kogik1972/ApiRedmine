from redmine.redmine_client import actualizar_estado_issue

from utils.logging_config import configurar_logging
import logging
configurar_logging()

def cerrar_issue_firma(issue_id, estado):
    """
    Actualiza el estado de un issue en Redmine después del proceso de firma.

    Args:
        issue_id (int): ID del issue en Redmine.
        estado (str): "firmado" o "rechazado"
    """
    try:
        logging.info(f"redmine_cierre.py - Iniciando cierre de issue {issue_id} con estado {estado}")

        # Mapeo interno de estado a status_id de Redmine
        if estado == "firmado":
            status_id = 14  # Los firmantes han aceptado firmar el respectivo documento
        elif estado == "rechazado":
            status_id = 15  # Uno o Todos los firmantes han rechazado firmar el respectivo documento
        else:
            logging.error(f"redmine_cierre.py - Estado desconocido: {estado}")
            return False

        actualizar_estado_issue(issue_id, status_id)
        logging.info(f"redmine_cierre.py - Issue {issue_id} actualizado correctamente a estado {estado}")
        return True

    except Exception as e:
        logging.error(f"redmine_cierre.py - Error cerrando issue {issue_id}: {e}", exc_info=True)
        return False
