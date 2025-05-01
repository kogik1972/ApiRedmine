## firma_mailer.py
import os
from flask import Flask
from flask_mail import Mail, Message
from firma.firma_utils import crear_link_firma
import smtplib
from email.message import EmailMessage

from utils.logging_config import configurar_logging
import logging
configurar_logging()
logger = logging.getLogger(__name__)

mail = Mail()  # Extensión global

def create_mail_app():
    """Crea una app mínima para el envío de correos usando Flask-Mail."""
    required_keys = ['MAIL_SERVER', 'MAIL_USERNAME', 'MAIL_PASSWORD', 'MAIL_DEFAULT_SENDER']
    for key in required_keys:
        if not os.getenv(key):
            raise RuntimeError(f"⚠️ Falta configuración de correo: {key} no está definido en el entorno")

    app = Flask(__name__)
    app.config.update({
        'MAIL_SERVER': os.getenv('MAIL_SERVER'),
        'MAIL_PORT': int(os.getenv('MAIL_PORT', 587)),
        'MAIL_USE_TLS': os.getenv('MAIL_USE_TLS', 'true').lower() == 'true',
        'MAIL_USERNAME': os.getenv('MAIL_USERNAME'),
        'MAIL_PASSWORD': os.getenv('MAIL_PASSWORD'),
        'MAIL_DEFAULT_SENDER': os.getenv('MAIL_DEFAULT_SENDER'),
    })
    mail.init_app(app)
    return app

def enviar_correo_firma(nombre_firmante, rut_firmante, tipo_firmante, email_firmante,
                        nombre_documento, path_documento, link_aceptar, link_rechazar):
    """Envía un correo con los enlaces únicos de firma y rechazo para un firmante (sin depender de SQLAlchemy)."""
    app = create_mail_app()

    with app.app_context():
        asunto = f"Firma requerida: {nombre_documento}"
        destinatario = email_firmante

        cuerpo_html = f"""..."""  # OMITIDO PARA BREVEDAD (idéntico al original)
        cuerpo_texto = f"""..."""  # OMITIDO PARA BREVEDAD

        msg = Message(
            subject=asunto,
            recipients=[destinatario],
            html=cuerpo_html,
            body=cuerpo_texto
        )

        if os.path.exists(path_documento):
            with open(path_documento, "rb") as file:
                msg.attach(
                    filename=nombre_documento,
                    content_type="application/pdf",
                    data=file.read()
                )
                logger.info(f"firma_mailer.py - Documento adjunto: {nombre_documento}")
        else:
            logger.warning(f"firma_mailer.py - Documento NO encontrado para adjuntar: {path_documento}")

        mail.send(msg)
        logger.info(f"firma_mailer.py - Correo enviado a: {destinatario}")

def enviar_docx_final(nombre, email, documento_path, documento_nombre):
    """
    Envía un correo electrónico con un documento .docx firmado adjunto.
    """
    try:
        logger.info(f"firma_mailer - Iniciando envío de documento firmado a {email}")

        servidor_smtp = os.getenv("MAIL_SERVER")
        puerto_smtp = int(os.getenv("MAIL_PORT", 587))
        email_origen = os.getenv("MAIL_DEFAULT_SENDER")
        password_origen = os.getenv("MAIL_PASSWORD")

        if not all([servidor_smtp, puerto_smtp, email_origen, password_origen]):
            logger.error("firma_mailer - Configuración SMTP incompleta en variables de entorno")
            return False

        msg = EmailMessage()
        msg['Subject'] = "Documento firmado electrónicamente"
        msg['From'] = email_origen
        msg['To'] = email
        msg.set_content(f"Estimado/a {nombre},\n\nAdjuntamos el documento firmado electrónicamente.\n\nSaludos cordiales.")

        ruta_completa = os.path.join(documento_path, documento_nombre)

        if not os.path.isfile(ruta_completa):
            logger.error(f"firma_mailer.py - Documento no encontrado para adjuntar: {ruta_completa}")
            return False

        with open(ruta_completa, 'rb') as f:
            file_data = f.read()
            file_name = documento_nombre

        msg.add_attachment(
            file_data,
            maintype='application',
            subtype='vnd.openxmlformats-officedocument.wordprocessingml.document',
            filename=file_name
        )

        with smtplib.SMTP(servidor_smtp, puerto_smtp) as smtp:
            smtp.starttls()
            smtp.login(email_origen, password_origen)
            smtp.send_message(msg)

        logger.info(f"firma_mailer.py - Documento firmado enviado exitosamente a {email}")
        return True

    except Exception as e:
        logger.error(f"firma_mailer.py - Error enviando documento firmado a {email}: {e}", exc_info=True)
        return False
