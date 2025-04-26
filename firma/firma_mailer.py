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


def enviar_correo_firma(firma, documento):
    """Envia un correo con los enlaces únicos de firma y rechazo para un firmante."""
    app = create_mail_app()

    with app.app_context():
        link_aceptar = crear_link_firma(firma.token, 'aceptar')
        link_rechazar = crear_link_firma(firma.token, 'rechazar')

        asunto = f"Firma requerida: {documento.nombre}"
        destinatario = firma.email

        cuerpo_html = f"""
        <html>
        <head>
            <style>
                .body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; }}
                .btn {{
                    display: inline-block;
                    padding: 12px 24px;
                    text-decoration: none;
                    border-radius: 4px;
                    font-weight: bold;
                    color: white !important;
                    font-size: 15px;
                }}
                .btn-aceptar {{ background-color: #28a745; }}
                .btn-rechazar {{ background-color: #dc3545; margin-left: 10px; }}
                .footer {{ margin-top: 20px; font-size: 0.9em; color: #6c757d; }}
            </style>
        </head>
        <body class="body">
            <p>Estimado/a <strong>{firma.nombre}</strong> ({firma.rut}),</p>
            <p>Ha sido asignado como <strong>{firma.tipo}</strong> y se requiere su firma electrónica para el documento:</p>
            <p><strong>{documento.nombre}</strong></p>
            <div style="margin: 25px 0;">
                <a href="{link_aceptar}" class="btn btn-aceptar">✅ Aceptar y Firmar</a>
                <a href="{link_rechazar}" class="btn btn-rechazar">❌ Rechazar Documento</a>
            </div>
            <p class="footer">Este enlace es único y no debe compartirse.<br>
            Atentamente,<br>El equipo de Condominium</p>
        </body>
        </html>
        """

        cuerpo_texto = f"""Estimado/a {firma.nombre} ({firma.rut}),

Ha sido asignado como {firma.tipo} y se requiere su firma electrónica para el documento: {documento.nombre}

✔️ Firmar: {link_aceptar}
❌ Rechazar: {link_rechazar}

Este enlace es único y no debe compartirse.

Atentamente,
El equipo de Condominium
"""

        msg = Message(
            subject=asunto,
            recipients=[destinatario],
            html=cuerpo_html,
            body=cuerpo_texto
        )

        # Adjuntar el archivo PDF al correo
        doc_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', documento.path_pdf))
        nombre_archivo = os.path.basename(doc_path)

        if os.path.exists(doc_path):
            with open(doc_path, "rb") as file:
                msg.attach(
                    filename=nombre_archivo,
                    content_type="application/pdf",
                    data=file.read()
                )
                print(f"📎 Documento adjunto: {nombre_archivo}")
        else:
            print(f"⚠ Advertencia: No se encontró el documento a adjuntar: {doc_path}")

        mail.send(msg)
        print(f"📨 Correo enviado a: {destinatario}")


def enviar_docx_final(nombre, email, documento_path, documento_nombre):
    """
    Envía un correo electrónico con un documento .docx firmado adjunto.

    Args:
        nombre (str): Nombre del destinatario.
        email (str): Email del destinatario.
        documento_path (str): Ruta donde se encuentra el documento.
        documento_nombre (str): Nombre del documento a adjuntar.
    """

    try:
        logging.info(f"firma_mailer - Iniciando envío de documento firmado a {email}")

        # Configuración SMTP desde variables de entorno
        servidor_smtp = os.getenv("MAIL_SERVER")  # Ejemplo: "smtp.gmail.com"
        puerto_smtp = int(os.getenv("MAIL_PORT", 587))  # Puerto estándar TLS
        email_origen = os.getenv("MAIL_DEFAULT_SENDER")  # Ejemplo: "firma@example.com"
        password_origen = os.getenv("MAIL_PASSWORD")

        if not all([servidor_smtp, puerto_smtp, email_origen, password_origen]):
            logging.error("firma_mailer - Configuración SMTP incompleta en variables de entorno")
            return False

        # Crear mensaje de correo
        msg = EmailMessage()
        msg['Subject'] = "Documento firmado electrónicamente"
        msg['From'] = email_origen
        msg['To'] = email
        msg.set_content(f"Estimado/a {nombre},\n\nAdjuntamos el documento firmado electrónicamente.\n\nSaludos cordiales.")

        # Cargar y adjuntar el archivo
        ruta_completa = os.path.join(documento_path, documento_nombre)

        if not os.path.isfile(ruta_completa):
            logging.error(f"firma_mailer - Documento no encontrado para adjuntar: {ruta_completa}")
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

        # Enviar el correo
        with smtplib.SMTP(servidor_smtp, puerto_smtp) as smtp:
            smtp.starttls()
            smtp.login(email_origen, password_origen)
            smtp.send_message(msg)

        logging.info(f"firma_mailer - Documento firmado enviado exitosamente a {email}")
        return True

    except Exception as e:
        logging.error(f"firma_mailer - Error enviando documento firmado a {email}: {e}", exc_info=True)
        return False