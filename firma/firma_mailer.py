# firma/firma_mailer.py
import os
from flask import Flask
from flask_mail import Mail, Message
from firma.firma_utils import crear_link_firma
import smtplib
from email.message import EmailMessage
import logging

mail = Mail()  # Extensión global

def create_mail_app():
    required_keys = ['MAIL_SERVER', 'MAIL_USERNAME', 'MAIL_PASSWORD', 'MAIL_DEFAULT_SENDER']
    for key in required_keys:
        if not os.getenv(key):
            raise RuntimeError(f"⚠️ firma_mailer - Falta configuración de correo: {key} no está definido en el entorno")

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

def enviar_correo_firma(firma, documento):
    app = create_mail_app()

    with app.app_context():
        link_aceptar = crear_link_firma(firma.token, 'aceptar')
        link_rechazar = crear_link_firma(firma.token, 'rechazar')

        asunto = f"Firma requerida: {documento.nombre}"
        destinatario = firma.email
        logging.info(f"firma_mailer - Preparando correo de firma para: {destinatario}")

        cuerpo_html = f"""
        <html>... (contenido HTML omitido para brevedad) ...</html>
        """

        cuerpo_texto = f"""Estimado/a {firma.nombre} ({firma.rut}), ..."""

        msg = Message(
            subject=asunto,
            recipients=[destinatario],
            html=cuerpo_html,
            body=cuerpo_texto
        )

        doc_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', documento.path_pdf))
        nombre_archivo = os.path.basename(doc_path)

        if os.path.exists(doc_path):
            with open(doc_path, "rb") as file:
                msg.attach(
                    filename=nombre_archivo,
                    content_type="application/pdf",
                    data=file.read()
                )
                logging.info(f"firma_mailer - 📎 Documento adjunto: {nombre_archivo}")
        else:
            logging.warning(f"firma_mailer - ⚠ No se encontró el documento a adjuntar: {doc_path}")

        mail.send(msg)
        logging.info(f"firma_mailer - 📨 Correo enviado a: {destinatario}")

def enviar_docx_final(documento, ruta_docx):
    try:
        remitente = os.getenv("MAIL_FROM")
        destinatario = documento.responsable_email
        asunto = f"Documento firmado: {documento.nombre_archivo}"
        cuerpo = f"""Estimado/a {documento.nombre_responsable}, ..."""

        mensaje = EmailMessage()
        mensaje["Subject"] = asunto
        mensaje["From"] = remitente
        mensaje["To"] = destinatario
        mensaje.set_content(cuerpo)

        with open(ruta_docx, "rb") as f:
            contenido = f.read()
            nombre_archivo = os.path.basename(ruta_docx)
            mensaje.add_attachment(contenido, maintype="application", subtype="vnd.openxmlformats-officedocument.wordprocessingml.document", filename=nombre_archivo)

        servidor = os.getenv("MAIL_SERVER")
        puerto = int(os.getenv("MAIL_PORT", 25))
        with smtplib.SMTP(servidor, puerto) as smtp:
            smtp.send_message(mensaje)

        logging.info(f"firma_mailer - 📤 Correo con documento firmado enviado a {destinatario}")

    except Exception as e:
        logging.error(f"firma_mailer - ❌ Error al enviar correo con documento firmado: {e}")
