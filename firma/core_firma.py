# firma/core_firma.py
import sys
import os

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import argparse
from flask import Flask
from dotenv import load_dotenv
from scripts.archivo_manager import mover_a_docs
from redmine.redmine_client import obtener_emails_desde_redmine
from app import db
from db.db_models import Documento
from firma.firma_utils import registrar_firmante
from firma.firma_mailer import enviar_correo_firma


def parse_args():
    parser = argparse.ArgumentParser(description="Core de orquestación del proceso de firma electrónica.")
    parser.add_argument('--issue_id', type=int, required=True, help='ID del issue en Redmine')
    parser.add_argument('--directorio', type=str, required=True, help='Directorio donde se generó el archivo')
    parser.add_argument('--nombre_documento', type=str, required=True, help='Nombre del archivo PDF generado')
    return parser.parse_args()


def create_app():
    app = Flask(__name__)
    load_dotenv()
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    return app


def main():
    args = parse_args()
    app = create_app()

    with app.app_context():
        db.create_all()  # asegúrate de que las tablas estén listas

        ruta_original = os.path.join(ROOT_DIR, args.directorio, args.nombre_documento)

        if not os.path.isfile(ruta_original):
            print(f"❌ Archivo no encontrado: {ruta_original}")
            return

        ruta_final, nombre_final = mover_a_docs(ruta_original, args.nombre_documento)

        datos_firmantes = obtener_emails_desde_redmine(args.issue_id)
        if not datos_firmantes:
            print("❌ No se pudieron obtener los datos de los firmantes. Proceso abortado.")
            return

        # 1. Registrar documento
        documento = Documento(
            nombre=nombre_final,
            path_pdf=os.path.join("docs", nombre_final),
            issue_id=args.issue_id
        )
        db.session.add(documento)
        db.session.commit()

        # 2. Registrar firmantes y enviar correos
        for tipo, persona in datos_firmantes.items():
            resultado = registrar_firmante(
                documento_id=documento.id,
                nombre=persona["nombre"],
                rut=persona["rut"],
                email=persona["email"],
                tipo=tipo,
                issue_id=args.issue_id
            )
            firmante = resultado["firma"]
            enviar_correo_firma(firmante, documento)

        print(f"✅ Documento registrado en BD con ID {documento.id}")
        print(f"📧 Correos enviados a: {', '.join(p['email'] for p in datos_firmantes.values())}")

if __name__ == '__main__':
    main()
