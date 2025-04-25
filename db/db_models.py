## db/db_models.py
from flask import Blueprint, render_template, request
from app import db
from db.db_models import FirmaRequerida
from itsdangerous import URLSafeSerializer
from datetime import datetime, timezone
from dotenv import load_dotenv
import os
import traceback
import pytz
import logging

# Lógica de firma
from firma.cerrar_firma import cerrar_aprobado, cerrar_rechazado

# Cargar variables de entorno
load_dotenv()

# Blueprint
respuestas_bp = Blueprint('respuestas', __name__)

# Serializador
SECRET_KEY = os.getenv("SECRET_KEY")
serializer = URLSafeSerializer(SECRET_KEY)

@respuestas_bp.route("/firmar", methods=["GET"], strict_slashes=False)
def procesar_respuesta():
    try:
        token = request.args.get("token")
        accion = request.args.get("accion")
        logging.info(f"respuestas - Solicitud recibida: token={token}, accion={accion}")

        if not token or not accion:
            logging.warning("respuestas - Faltan parámetros requeridos en la solicitud")
            return "Faltan parámetros requeridos", 400

        data = serializer.loads(token)
        firma_id = data.get("firma_id")
        logging.info(f"respuestas - Token decodificado para firma_id={firma_id}")

        if data.get("accion") != accion:
            logging.warning("respuestas - Acción del token no coincide con la acción recibida")
            return "La acción no coincide con el token", 400

        firma = FirmaRequerida.query.get(firma_id)
        if not firma:
            logging.error(f"respuestas - Firma no encontrada para ID {firma_id}")
            return "Firma no encontrada", 404

        if firma.estado in ['aceptado', 'rechazado']:
            logging.info(f"respuestas - Firma ID {firma.id} ya respondida con estado {firma.estado}")
            return render_template("ya_respondido.html", estado=firma.estado)

        firma.estado = "aceptado" if accion == "aceptar" else "rechazado"
        tz_cl = pytz.timezone('America/Santiago')
        firma.fecha_firma = datetime.now(tz_cl)
        db.session.commit()
        logging.info(f"respuestas - Estado actualizado para firma ID {firma.id}: {firma.estado}")

        documento = firma.documento
        estados = [f.estado for f in documento.firmas]

        if "rechazado" in estados:
            logging.info(f"respuestas - Documento {documento.id} marcado como rechazado. Ejecutando cierre...")
            documento.estado_firma = "rechazado"
            db.session.commit()
            cerrar_rechazado(documento)

        elif all(e == "aceptado" for e in estados):
            logging.info(f"respuestas - Todas las firmas aceptadas para documento {documento.id}. Ejecutando cierre aprobado...")
            documento.estado_firma = "firmado"
            db.session.commit()
            cerrar_aprobado(documento)

        return render_template("gracias.html", estado=firma.estado)

    except Exception as e:
        logging.error(f"respuestas - ❌ Error al procesar respuesta de firma: {e}")
        return f"<pre>{traceback.format_exc()}</pre>", 500
