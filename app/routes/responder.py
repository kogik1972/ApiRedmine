from flask import Blueprint, render_template, request
from app import db
from db.db_models import FirmaRequerida
from itsdangerous import URLSafeSerializer
from datetime import datetime
from dotenv import load_dotenv
import os
import traceback
import pytz
import logging

from utils.logging_config import configurar_logging
configurar_logging()
logger = logging.getLogger(__name__)

from utils.convertidor import convierto_docx2pdf
from utils.convertidor_sql import actualiza_sql

# Cargar variables de entorno
load_dotenv()

# Blueprint
respuestas_bp = Blueprint('respuestas', __name__)

# Serializador
SECRET_KEY = os.getenv("SECRET_KEY")
serializer = URLSafeSerializer(SECRET_KEY)

# Funciones de procesamiento
from firmar.estampar_firmas import estampar_firmas
from firmar.firmar_cierre import enviar_documento_firmado
from redmine.redmine_cierre import cerrar_issue_firma

@respuestas_bp.route("/firmar", methods=["GET"], strict_slashes=False)
def procesar_respuesta():
    try:
        token = request.args.get("token")
        accion = request.args.get("accion")

        if not token or not accion:
            logger.warning("Faltan parámetros requeridos")
            return "Faltan parámetros requeridos", 400

        data = serializer.loads(token)
        firma_id = data.get("firma_id")

        if data.get("accion") != accion:
            logger.warning("Acción no coincide con token")
            return "La acción no coincide con el token", 400

        firma = FirmaRequerida.query.get(firma_id)
        if not firma:
            logger.error(f"Firma no encontrada: {firma_id}")
            return "Firma no encontrada", 404

        if firma.estado in ['aceptado', 'rechazado']:
            logger.info(f"Firma ya respondida: {firma.estado}")
            return render_template("ya_respondido.html", estado=firma.estado)

        # Actualizar estado de la firma
        firma.estado = "aceptado" if accion == "aceptar" else "rechazado"
        tz_cl = pytz.timezone('America/Santiago')
        firma.fecha_firma = datetime.now(tz_cl)
        db.session.commit()

        documento = firma.documento
        estados = [f.estado for f in documento.firmas]
        issue_id = documento.issue_id
        nombre_documento = documento.nombre
        path_documento = documento.path_pdf
        firmas_requeridas = documento.firmas
        destinatarios = [{'nombre': f.nombre, 'email': f.email} for f in firmas_requeridas]
        token_documento = documento.token_documento

        path_documento = os.path.dirname(path_documento)

        if "rechazado" in estados:
            documento.estado_firma = "rechazado"
            resultado_cierre = cerrar_issue_firma(issue_id, "rechazado")
            if not resultado_cierre:
                raise Exception("Error al rechazar issue en Redmine")

        elif all(e == "aceptado" for e in estados):
            documento.estado_firma = "firmado"
            logger.info(f"nombre_documento: {nombre_documento}")

            resultado_estampado = estampar_firmas(
                issue_id,
                nombre_documento,
                path_documento,
                firmas_requeridas,
                token_documento
            )
            if not resultado_estampado:
                raise Exception("Error al estampar firmas")

            nombre_documento_pdf = convierto_docx2pdf(nombre_documento, path_documento)
            if not nombre_documento_pdf:
                raise Exception("Error al convertir en PDF")

            resultado = actualiza_sql(nombre_documento, nombre_documento_pdf, path_documento)
            logger.info(f"actualiza_sql: {resultado} {nombre_documento_pdf}")

            resultado_envio = enviar_documento_firmado(
                issue_id, path_documento, nombre_documento_pdf, destinatarios
            )
            if not resultado_envio:
                raise Exception("Error al enviar documento firmado")

            resultado_cierre = cerrar_issue_firma(issue_id, "firmado")
            if not resultado_cierre:
                raise Exception("Error al cerrar issue firmado")

        db.session.commit()
        return render_template("gracias.html", estado=firma.estado)

    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return f"<pre>{traceback.format_exc()}</pre>", 500
