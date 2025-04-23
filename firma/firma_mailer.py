# firma/firma_mailer.py

import os
from flask import Flask
from flask_mail import Mail, Message
from dotenv import load_dotenv
from firma.firma_utils import crear_link_firma

load_dotenv()

mail = Mail()  # Extensión global

def create_mail_app():
    app = Flask(__name__)
    app.config.update({
        'MAIL_SERVER': os.getenv('MAIL_SERVER'),
        'MAIL_PORT': int(os.getenv('MAIL_PORT', 587)),
        'MAIL_USE_TLS': os.getenv('MAIL_USE_TLS', 'true').lower() == 'true',
        'MAIL_USERNAME': os.getenv('MAIL_USERNAME'),
        'MAIL_PASSWORD': os.getenv('MAIL_PASSWORD'),
        'MAIL_DEFAULT_SENDER': os.getenv('MAIL_DEFAULT_SENDER'),
    })
    mail.init_app(app)  # Se registra aquí correctamente
    return app


def enviar_correo_firma(firma, documento):
    app = create_mail_app()

    with app.app_context():  # 👈 TODO ocurre DENTRO del contexto

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

        # Adjuntar PDF
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
            print(f"⚠ No se encontró el documento a adjuntar: {doc_path}")

        mail.send(msg)
        print(f"📨 Correo enviado a: {destinatario}")
