## respuestas.py
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

from utils.convertidor import convierto_docx2pdf

# Cargar variables de entorno
load_dotenv()

# Blueprint
respuestas_bp = Blueprint('respuestas', __name__)

# Serializador
SECRET_KEY = os.getenv("SECRET_KEY")
serializer = URLSafeSerializer(SECRET_KEY)

# Importar funciones de estampado, envío y cierre
from firma.estampar_firmas import estampar_firmas
from firma.firma_cierre import enviar_documento_firmado
from redmine.redmine_cierre import cerrar_issue_firma

@respuestas_bp.route("/firmar", methods=["GET"], strict_slashes=False)
def procesar_respuesta():
    try:
        # Obtener token y acción desde parámetros de query
        token = request.args.get("token")
        accion = request.args.get("accion")

        if not token or not accion:
            logging.warning("respuestas.py - Faltan parámetros requeridos en la solicitud")
            return "Faltan parámetros requeridos", 400

        # Decodificar el token
        data = serializer.loads(token)
        firma_id = data.get("firma_id")

        # Validación cruzada entre token y parámetro
        if data.get("accion") != accion:
            logging.warning("respuestas.py - La acción no coincide con el token")
            return "La acción no coincide con el token", 400

        # Buscar firmante
        firma = FirmaRequerida.query.get(firma_id)
        if not firma:
            logging.error(f"respuestas.py - Firma no encontrada para firma_id: {firma_id}")
            return "Firma no encontrada", 404

        # Ya respondió
        if firma.estado in ['aceptado', 'rechazado']:
            logging.info(f"respuestas.py - Firma ya respondida previamente con estado: {firma.estado}")
            return render_template("ya_respondido.html", estado=firma.estado)

        # Actualizar estado
        firma.estado = "aceptado" if accion == "aceptar" else "rechazado"
        tz_cl = pytz.timezone('America/Santiago')
        firma.fecha_firma = datetime.now(tz_cl)
        db.session.commit()

        # Verificar estado general del documento
        documento = firma.documento
        estados = [f.estado for f in documento.firmas]

        # Preparar datos
        issue_id = documento.issue_id
        nombre_documento = documento.nombre
        path_documento = documento.path_pdf
        firmas_requeridas = [f for f in documento.firmas]
        #destinatarios = [f.email for f in documento.firmas]
        destinatarios = [{'nombre': f.nombre, 'email': f.email} for f in documento.firmas]

        logging.info(f"respuestas.py - issue_id: {issue_id}")
        logging.info(f"respuestas.py - nombre_documento: {nombre_documento}")
        logging.info(f"respuestas.py - path_documento sucio: {path_documento}")

        path_documento = os.path.dirname(path_documento)

        logging.info(f"respuestas.py - path_documento limpio: {path_documento}")

        if "rechazado" in estados:
            documento.estado_firma = "rechazado"
            logging.info(f"respuestas.py - Documento marcado como rechazado. Cerrando issue {issue_id} en Redmine.")
            #3) Cerrar issue en Redmine
            resultado_cierre = cerrar_issue_firma(issue_id, "rechazado")
            if not resultado_cierre:
                logging.error(f"respuestas.py - Error al rechazar issue {issue_id} en Redmine")
                raise Exception("Error al rechazar issue en Redmine")

        elif all(e == "aceptado" for e in estados):
            documento.estado_firma = "firmado"
            logging.info(f"respuestas.py - Todas las firmas aceptadas. Estampando documento: {nombre_documento}.")

            # 1) Estampar firmas
            resultado_estampado = estampar_firmas(issue_id, nombre_documento, path_documento, firmas_requeridas)
            if not resultado_estampado:
                logging.error(f"respuestas.py - Error al estampar firmas en documento {nombre_documento}")
                raise Exception("Error al estampar firmas")

            # 2) Transformo documento firmado en pdf
            nombre_documento_pdf = convierto_docx2pdf(nombre_documento, path_documento) 
            if not nombre_documento_pdf:
                logging.error(f"respuestas.py - Error al convertir en pdf {nombre_documento}")
                raise Exception("Error al convertir en pdf")
            
            logging.error(f"IMPORTANTE: {nombre_documento} {nombre_documento_pdf} {path_documento}")

            # 3) Enviar documento firmado
            resultado_envio = enviar_documento_firmado(issue_id, path_documento, nombre_documento_pdf, destinatarios)
            if not resultado_envio:
                logging.error(f"respuestas.py - Error al enviar documento firmado {nombre_documento_pdf}")
                raise Exception("Error al enviar documento firmado")

            # 4) Cerrar issue en Redmine
            resultado_cierre = cerrar_issue_firma(issue_id, "firmado")
            if not resultado_cierre:
                logging.error(f"respuestas.py - Error al cerrar issue {issue_id} en Redmine tras firma")
                raise Exception("Error al cerrar issue en Redmine")

        db.session.commit()

        logging.info(f"respuestas.py - Proceso completado correctamente para issue_id: {issue_id}")
        return render_template("gracias.html", estado=firma.estado)

    except Exception as e:
        logging.error(f"respuestas.py - Error general en procesar_respuesta: {e}")
        return f"<pre>{traceback.format_exc()}</pre>", 500