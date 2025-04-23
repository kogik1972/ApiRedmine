# firma/core_firma.py

import sys
import os

# Define la raíz absoluta del proyecto para asegurar importaciones correctas
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

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
    """Parsea los argumentos requeridos para ejecutar el script."""
    parser = argparse.ArgumentParser(description="Core de orquestación del proceso de firma electrónica.")
    parser.add_argument('--issue_id', type=int, required=True, help='ID del issue en Redmine')
    parser.add_argument('--directorio', type=str, required=True, help='Directorio donde se generó el archivo')
    parser.add_argument('--nombre_documento', type=str, required=True, help='Nombre del archivo PDF generado')
    return parser.parse_args()


def main():
    """Punto de entrada principal del proceso de firma electrónica."""
    args = parse_args()

    # Crea instancia Flask y configura conexión a base de datos
    app = create_app()

    # Asegura que la base y el contexto estén disponibles
    with app.app_context():
        db.create_all()  # Se asegura que las tablas existen (no recrea si ya están)

    # Construye la ruta completa al archivo original
    ruta_original = os.path.join(ROOT_DIR, args.directorio, args.nombre_documento)

    if not os.path.isfile(ruta_original):
        print(f"❌ Archivo no encontrado: {ruta_original}")
        return

    # Mueve el archivo a la carpeta /docs/, evitando colisiones
    ruta_final, nombre_final = mover_a_docs(ruta_original, args.nombre_documento)

    # Obtiene los firmantes desde Redmine a través del issue_id
    datos_firmantes = obtener_emails_desde_redmine(args.issue_id)
    if not datos_firmantes:
        print("❌ No se pudieron obtener los datos de los firmantes. Proceso abortado.")
        return

    with app.app_context():
        # 1. Registrar el documento en la base
        documento = Documento(
            nombre=nombre_final,
            path_pdf=os.path.join("docs", nombre_final)
        )
        db.session.add(documento)
        db.session.commit()

        # 2. Registrar cada firmante y enviar correo
        for tipo, persona in datos_firmantes.items():
            token = registrar_firmante(
                documento_id=documento.id,
                nombre=persona["nombre"],
                rut=persona["rut"],
                email=persona["email"],
                tipo=tipo
            )

            # Se asume que registrar_firmante agrega la firma al documento
            firmante = documento.firmas[-1]
            enviar_correo_firma(firmante, documento)

        print(f"✅ Documento registrado en BD con ID {documento.id}")
        print(f"📧 Correos enviados a: {', '.join(p['email'] for p in datos_firmantes.values())}")


if __name__ == '__main__':
    main()
