import logging
from firma.firma_mailer import enviar_docx_final

def enviar_documento_firmado(issue_id, documento_path, documento_nombre, destinatarios):
    """
    Orquesta el envío de un documento firmado electrónicamente a una lista de destinatarios.
    Usa internamente firma_mailer.

    Args:
        issue_id (int): ID del issue asociado.
        documento_path (str): Ruta completa donde está el documento.
        documento_nombre (str): Nombre del documento.
        destinatarios (list): Lista de diccionarios con 'nombre' y 'email'.
    """
    try:
        logging.info(f"firma_cierre - Iniciando envío de documento firmado para issue {issue_id}")

        for destinatario in destinatarios:
            nombre = destinatario.get('nombre')
            email = destinatario.get('email')

            if not email:
                logging.warning(f"firma_cierre - Email no disponible para {nombre}, se omite envío")
                continue

            enviar_docx_final(
                nombre,
                email,
                documento_path,
                documento_nombre
            )

            logging.info(f"firma_cierre - Documento enviado correctamente a {email}")

        logging.info(f"firma_cierre - Envío de documentos finalizado para issue {issue_id}")
        return True

    except Exception as e:
        logging.error(f"firma_cierre - Error enviando documento firmado para issue {issue_id}: {e}", exc_info=True)
        return False
