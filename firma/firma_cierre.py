## firma_cierre.py
from firma.firma_mailer import enviar_docx_final

from utils.logging_config import configurar_logging
import logging
configurar_logging()
logger = logging.getLogger(__name__)

def enviar_documento_firmado(issue_id, documento_path, documento_nombre, destinatarios):
    """
    Orquesta el envío de un documento firmado electrónicamente a una lista de destinatarios.
    Usa internamente firma_mailer.
    """
    try:
        logger.info(f"Iniciando envío de documento firmado para issue")
        logger.info(f"issue_id: {issue_id}")
        logger.info(f"documento_path: {documento_path}")
        logger.info(f"documento_nombre: {documento_nombre}")

        for destinatario in destinatarios:
            nombre = destinatario.get('nombre')
            email = destinatario.get('email')

            if not email:
                logger.warning(f"Email no disponible para {nombre}, se omite envío")
                continue

            enviar_docx_final(
                nombre,
                email,
                documento_path,
                documento_nombre
            )

            logger.info(f"Documento enviado correctamente a {email}")

        logger.info(f"Envío de documentos finalizado para issue {issue_id}")
        return True

    except Exception as e:
        logger.error(f"Error enviando documento firmado para issue {issue_id}: {e}", exc_info=True)
        return False
