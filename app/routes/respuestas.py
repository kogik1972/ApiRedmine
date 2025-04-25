from flask import Blueprint, render_template, request
from app import db
from db.db_models import FirmaRequerida
from itsdangerous import URLSafeSerializer
from datetime import datetime, timezone
from dotenv import load_dotenv
import os
import traceback
import pytz

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
        # Obtener token y acción desde parámetros de query
        token = request.args.get("token")
        accion = request.args.get("accion")

        if not token or not accion:
            return "Faltan parámetros requeridos", 400

        # Decodificar el token
        data = serializer.loads(token)
        firma_id = data.get("firma_id")

        # Validación cruzada entre token y parámetro
        if data.get("accion") != accion:
            return "La acción no coincide con el token", 400

        # Buscar firmante
        firma = FirmaRequerida.query.get(firma_id)
        if not firma:
            return "Firma no encontrada", 404

        # Ya respondió
        if firma.estado in ['aceptado', 'rechazado']:
            return render_template("ya_respondido.html", estado=firma.estado)

        # Actualizar estado
        firma.estado = "aceptado" if accion == "aceptar" else "rechazado"
        tz_cl = pytz.timezone('America/Santiago')
        firma.fecha_firma = datetime.now(tz_cl)
        db.session.commit()

        # Verificar estado general del documento
        documento = firma.documento
        estados = [f.estado for f in documento.firmas]

        if "rechazado" in estados:
            documento.estado_firma = "rechazado"
            db.session.commit()
            cerrar_rechazado(documento)

        elif all(e == "aceptado" for e in estados):
            documento.estado_firma = "firmado"
            db.session.commit()
            cerrar_aprobado(documento)

        return render_template("gracias.html", estado=firma.estado)

    except Exception as e:
        return f"<pre>{traceback.format_exc()}</pre>", 500
