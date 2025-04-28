import logging
from firma.firma_mailer import enviar_docx_final

from utils.logging_config import configurar_logging
import logging
configurar_logging()

def enviar_documento_firmado(issue_id, documento_path, documento_nombre, destinatarios):

    """
    Orquesta el envío de un documento firmado electrónicamente a una lista de destinatarios.
    Usa internamente firma_mailer.
   """
    try:
        logging.info(f"firma_cierre.py - Iniciando envío de documento firmado para issue")
        logging.info(f"firma_cierre.py - issue_id: {issue_id}")
        logging.info(f"firma_cierre.py - documento_path: {documento_path}")
        logging.info(f"firma_cierre.py - documento_nombre: {documento_nombre}")

        for destinatario in destinatarios:
            nombre = destinatario.get('nombre')
            email = destinatario.get('email')

            if not email:
                logging.warning(f"firma_cierre.py - Email no disponible para {nombre}, se omite envío")
                continue

            enviar_docx_final(
                nombre,
                email,
                documento_path,
                documento_nombre
            )

            logging.info(f"firma_cierre.py - Documento enviado correctamente a {email}")

        logging.info(f"firma_cierre.py - Envío de documentos finalizado para issue {issue_id}")
        return True

    except Exception as e:
        logging.error(f"firma_cierre.py - Error enviando documento firmado para issue {issue_id}: {e}", exc_info=True)
        return False
