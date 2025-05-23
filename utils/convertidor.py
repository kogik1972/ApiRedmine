## convertidor.py
import os
import subprocess

from utils.logging_config import configurar_logging
import logging
configurar_logging()
logger = logging.getLogger(__name__)

def convierto_docx2pdf(nombre_documento, path_documento):
    docx_path = os.path.join(path_documento, nombre_documento)

    if not os.path.isfile(docx_path):
        logger.info(f"Archivo no encontrado: {docx_path}")
        return None

    # Directorio de salida (el mismo que el del archivo DOCX)
    output_dir = os.path.dirname(docx_path)

    # Comando para convertir el archivo usando LibreOffice
    command = ['/usr/bin/soffice', '--headless', '--convert-to', 'pdf', docx_path, '--outdir', output_dir]

    # Asegura que el entorno incluya PATHs necesarios para comandos como grep, sed, etc.
    env = os.environ.copy()
    env["PATH"] += os.pathsep + "/usr/bin:/bin:/usr/local/bin"

    try:
        # Usa LibreOffice para convertir el DOCX a PDF
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)

        logger.info(f"Stdout: {result.stdout.decode()}")
        logger.info(f"Stderr: {result.stderr.decode()}")

        nombre_sin_extension = os.path.splitext(nombre_documento)[0]
        nombre_documento_pdf = f"{nombre_sin_extension}.pdf"
        return nombre_documento_pdf

    except subprocess.CalledProcessError as e:
        logger.critical(f'Ocurrió un error durante la conversión: {e.stderr.decode()}')
        return "500"
    except Exception as e:
        logger.critical(f'Ocurrió un error: {e}')
        return "500"