## core_firma.py

import sys
import os

# Define la raíz absoluta del proyecto para asegurar importaciones correctas
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from utils.logging_config import configurar_logging
import logging
configurar_logging()

import argparse

from scripts.archivo_manager import mover_a_docs
from redmine.redmine_client import obtener_emails_desde_redmine
from app import create_app, db
from db.db_models import Documento
from firma.firma_utils import registrar_firmante
from firma.firma_mailer import enviar_correo_firma

def parse_args():
    parser = argparse.ArgumentParser(description="Core de orquestación del proceso de firma electrónica.")
    parser.add_argument('--issue_id', type=int, required=True, help='ID del issue en Redmine')
    parser.add_argument('--directorio', type=str, required=True, help='Directorio donde se generó el archivo')
    parser.add_argument('--nombre_documento', type=str, required=True, help='Nombre del archivo generado')
    return parser.parse_args()

def main():
    logging.info('Punto de entrada principal del proceso de firma electrónica.')

    args = parse_args()
    app = create_app()

    with app.app_context():
        db.create_all()

    ruta_original = os.path.join(ROOT_DIR, args.directorio, args.nombre_documento)

    if not os.path.isfile(ruta_original):
        logging.error(f"Archivo no encontrado: {ruta_original}")
        return

    logging.info(f"args.issue_id: {args.issue_id}")
    logging.info(f"args.directorio: {args.directorio}")
    logging.info(f"args.nombre_documento: {args.nombre_documento}")

    ruta_final, nombre_final = mover_a_docs(ruta_original, args.nombre_documento)
    logging.info(f"ruta_final: {ruta_final}")
    logging.info(f"nombre_final: {nombre_final}")

    datos_firmantes = obtener_emails_desde_redmine(args.issue_id)
    if not datos_firmantes:
        logging.error("No se pudieron obtener los datos de los firmantes. Proceso abortado.")
        return

    with app.app_context():
        documento = Documento(
            nombre=nombre_final,
            path_pdf=os.path.join(args.directorio, ''),
            issue_id=args.issue_id
        )
        db.session.add(documento)
        db.session.commit()

        for tipo, persona in datos_firmantes.items():
            resultado = registrar_firmante(
                documento_id=documento.id,
                nombre=persona["nombre"],
                rut=persona["rut"],
                email=persona["email"],
                tipo=tipo
            )

            firma = resultado["firma"]
            link_aceptar = resultado["link_aceptar"]
            link_rechazar = resultado["link_rechazar"]

            logging.info(f"Link aceptar: {link_aceptar}")
            logging.info(f"Link rechazar: {link_rechazar}")

            enviar_correo_firma(firma, documento, link_aceptar, link_rechazar)

        logging.info(f"Documento registrado en BD con ID {documento.id}")
        logging.info(f"Correos enviados a: {', '.join(p['email'] for p in datos_firmantes.values())}")

if __name__ == '__main__':
    main()
