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
        logger.warning(f"Archivo no encontrado: {docx_path}")
        return None

    try:
        # Usa LibreOffice para convertir el DOCX a PDF
        subprocess.run([
            "libreoffice",
            "--headless",
            "--convert-to", "pdf",
            "--outdir", path_documento,
            docx_path
        ], check=True)

        nombre_sin_extension = os.path.splitext(nombre_documento)[0]
        nombre_documento_pdf = f"{nombre_sin_extension}.pdf"
        logger.info(f"Archivo convertido exitosamente: {nombre_documento_pdf}")
        return nombre_documento_pdf

    except subprocess.CalledProcessError as e:
        logger.error(f"Error al convertir el documento con LibreOffice: {e}", exc_info=True)
        return None
