## firma/core_firma.py

import sys
import os
import logging

# Define la raíz absoluta del proyecto para asegurar importaciones correctas
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# Configuración de logging
log_path = os.path.join(ROOT_DIR, "firma.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_path),
        logging.StreamHandler(sys.stdout)
    ]
)

# Librerías para CLI y entorno
import argparse
from dotenv import load_dotenv

# Funciones internas del sistema
from scripts.archivo_manager import mover_a_docs
from redmine.redmine_client import obtener_emails_desde_redmine
from app import create_app, db  # ✅ Usamos create_app global para consistencia
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
    args = parse_args()

    load_dotenv()
    logging.info(f"🚀 core_firma - Inicio de proceso de firma para issue #{args.issue_id}")
    logging.info(f"📂 core_firma - Archivo recibido: {args.nombre_documento} en {args.directorio}")

    app = create_app()

    with app.app_context():
        db.create_all()

    ruta_original = os.path.join(ROOT_DIR, args.directorio, args.nombre_documento)

    if not os.path.isfile(ruta_original):
        logging.error(f"❌ core_firma - Archivo no encontrado: {ruta_original}")
        return

    ruta_final, nombre_final = mover_a_docs(ruta_original, args.nombre_documento)
    logging.info(f"📎 core_firma - Archivo copiado a: {ruta_final}")

    datos_firmantes = obtener_emails_desde_redmine(args.issue_id)
    if not datos_firmantes:
        logging.error("❌ core_firma - No se pudieron obtener los datos de los firmantes. Proceso abortado.")
        return

    with app.app_context():
        documento = Documento(
            nombre=nombre_final,
            path_pdf=os.path.join("docs", nombre_final),
            issue_id=args.issue_id
        )
        db.session.add(documento)
        db.session.commit()
        logging.info(f"✅ core_firma - Documento registrado en BD con ID {documento.id}")

        for tipo, persona in datos_firmantes.items():
            logging.info(f"📝 core_firma - Registrando firmante {persona['nombre']} ({persona['email']}) como {tipo}")
            token = registrar_firmante(
                documento_id=documento.id,
                nombre=persona["nombre"],
                rut=persona["rut"],
                email=persona["email"],
                tipo=tipo
            )
            firmante = documento.firmas[-1]
            enviar_correo_firma(firmante, documento)
            logging.info(f"📧 core_firma - Correo enviado a {persona['email']}")

        logging.info("✅ core_firma - Proceso finalizado exitosamente.")

if __name__ == '__main__':
    main()
