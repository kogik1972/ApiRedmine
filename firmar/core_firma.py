## core_firma.py
import sys
import os
import secrets
from datetime import datetime
import pytz

# Define la raíz absoluta del proyecto para asegurar importaciones correctas
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from utils.logging_config import configurar_logging
import logging
configurar_logging()
logger = logging.getLogger(__name__)

# Librerías para CLI y entorno
import argparse

# Funciones internas del sistema
from scripts.archivo_manager import mover_a_docs
from redmine.redmine_client import obtener_emails_desde_redmine
from app import create_app, db
from db.db_models import Documento
from firmar.firmar_utils import registrar_firmante
from firmar.firmar_mailer import enviar_correo_firma

tz_cl = pytz.timezone('America/Santiago')

def generar_token_documento():
    return secrets.token_urlsafe(8)  # Ejemplo: 'XJ7Z-4F19'

def parse_args():
    """Parsea los argumentos requeridos para ejecutar el script."""
    parser = argparse.ArgumentParser(description="Core de orquestación del proceso de firma electrónica.")
    parser.add_argument('--issue_id', type=int, required=True, help='ID del issue en Redmine')
    parser.add_argument('--directorio', type=str, required=True, help='Directorio donde se generó el archivo')
    parser.add_argument('--nombre_documento', type=str, required=True, help='Nombre del archivo generado')
    return parser.parse_args()

def main():
    logger.info('Punto de entrada principal del proceso de firma electrónica.')

    args = parse_args()

    # Crea instancia Flask y configura conexión a base de datos
    app = create_app()

    # Asegura que la base y el contexto estén disponibles
    with app.app_context():
        db.create_all()  # Se asegura que las tablas existen (no recrea si ya están)

    # Construye la ruta completa al archivo original
    ruta_original = os.path.join(ROOT_DIR, args.directorio, args.nombre_documento)

    if not os.path.isfile(ruta_original):
        logger.error(f"Archivo no encontrado: {ruta_original}")
        return

    logger.info(f'args.issue_id: {args.issue_id}')
    logger.info(f'args.directorio: {args.directorio}')
    logger.info(f'args.nombre_documento: {args.nombre_documento}')

    # Mueve el archivo a la carpeta /docs/, evitando colisiones
    ruta_final, nombre_final = mover_a_docs(ruta_original, args.nombre_documento)
    logger.info(f'ruta_final: {ruta_final}')
    logger.info(f'nombre_final: {nombre_final}')

    # Obtiene los firmantes desde Redmine a través del issue_id
    datos_firmantes = obtener_emails_desde_redmine(args.issue_id)
    if not datos_firmantes:
        logger.error("No se pudieron obtener los datos de los firmantes. Proceso abortado.")
        return

    with app.app_context():
        # Registrar el documento en la base con token único
        token_doc = generar_token_documento()
        documento = Documento(
            nombre=args.nombre_documento,
            path_pdf=os.path.join(args.directorio, ''),
            issue_id=args.issue_id,
            token_documento=token_doc
        )
        db.session.add(documento)
        db.session.commit()
        logger.info(f"Documento registrado en BD con ID {documento.id} y token {token_doc}")

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

            logger.info(f"link aceptar: {link_aceptar}")
            logger.info(f"link rechazar: {link_rechazar}")

            enviar_correo_firma(
                nombre_firmante=firma.nombre,
                rut_firmante=firma.rut,
                tipo_firmante=firma.tipo,
                email_firmante=firma.email,
                nombre_documento=documento.nombre,
                path_documento=ruta_final,
                link_aceptar=link_aceptar,
                link_rechazar=link_rechazar
            )

        logger.info(f"Correos enviados a: {', '.join(p['email'] for p in datos_firmantes.values())}")

if __name__ == '__main__':
    main()
