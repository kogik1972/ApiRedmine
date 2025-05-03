import os
import logging
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO

from utils.logging_config import configurar_logging
configurar_logging()
logger = logging.getLogger(__name__)

def estampar_firmas_pdf(issue_id, nombre_documento, path_documento, firmas_requeridas, token_documento):
    try:
        logger.info(f"Estampando PDF para issue_id: {issue_id}")
        ruta_completa = os.path.join(path_documento, nombre_documento)

        if not os.path.isfile(ruta_completa):
            logger.error(f"Archivo no encontrado: {ruta_completa}")
            return False

        # Extraer firmas
        firmante = next((f for f in firmas_requeridas if f.tipo == 'firmante'), None)
        responsable = next((f for f in firmas_requeridas if f.tipo == 'responsable'), None)

        # Crear PDF en memoria con firmas y texto
        packet = BytesIO()
        can = canvas.Canvas(packet, pagesize=letter)
        can.setFont("Helvetica", 8)

        if firmante:
            can.drawString(50, 100, f"Trabajador: {firmante.nombre} {firmante.rut} {firmante.fecha_firma}")
        if responsable:
            can.drawRightString(550, 100, f"Empresa: {responsable.nombre} {responsable.rut} {responsable.fecha_firma}")

        can.setFont("Helvetica-Bold", 10)
        can.drawString(50, 80, "Este documento fue firmado electrónicamente.")
        can.setFont("Helvetica-Oblique", 10)
        can.drawString(50, 65, f"Código de validación: {token_documento}")
        can.setFont("Helvetica", 10)
        can.drawString(50, 50, "Puede verificar la autenticidad en:")
        can.setFillColorRGB(0, 0, 1)  # Azul
        can.drawString(50, 35, "https://condominium.eproc-chile.cl/validar")

        can.save()
        packet.seek(0)

        # Leer PDFs
        existing_pdf = PdfReader(ruta_completa)
        overlay_pdf = PdfReader(packet)
        output = PdfWriter()

        for page_num in range(len(existing_pdf.pages)):
            page = existing_pdf.pages[page_num]
            if page_num == len(existing_pdf.pages) - 1:
                # Solo en la última página estampamos
                page.merge_page(overlay_pdf.pages[0])
            output.add_page(page)

        # Guardar PDF modificado
        with open(ruta_completa, "wb") as outputStream:
            output.write(outputStream)

        logger.info(f"Estampado PDF completado: {ruta_completa}")
        return True

    except Exception as e:
        logger.error(f"Error al estampar firmas PDF: {e}", exc_info=True)
        return False
