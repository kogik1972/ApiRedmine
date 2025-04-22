from flask import Blueprint, render_template
from app import db
from db.db_models import FirmaRequerida
from itsdangerous import URLSafeSerializer
from datetime import datetime
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()

# Blueprint
respuestas_bp = Blueprint('respuestas', __name__)

# Serializador
SECRET_KEY = os.getenv("SECRET_KEY")
serializer = URLSafeSerializer(SECRET_KEY)

@respuestas_bp.route("/respuesta_firma/<token>", methods=["GET"])
def procesar_respuesta(token):
    try:
        # Decodificar el token
        data = serializer.loads(token)
        firma_id = data.get("firma_id")
        accion = data.get("accion")  # "aceptar" o "rechazar"

        # Buscar firmante
        firma = FirmaRequerida.query.get(firma_id)
        if not firma:
            return "Firma no encontrada", 404

        # Si ya respondió antes
        if firma.estado in ['aceptado', 'rechazado']:
            return render_template("ya_respondido.html", estado=firma.estado)

        # Actualizar estado
        firma.estado = "aceptado" if accion == "aceptar" else "rechazado"
        firma.fecha_respuesta = datetime.now()
        db.session.commit()

        # Verificar estado general del documento
        documento = firma.documento
        estados = [f.estado for f in documento.firmas]

        if "rechazado" in estados:
            documento.estado_firma = "no firmado"
        elif all(e == "aceptado" for e in estados):
            documento.estado_firma = "firmado"
            # 🔜 Aquí puedes llamar a estampado de PDF o envío de correo con documento firmado

        db.session.commit()
        return render_template("gracias.html", estado=firma.estado)

    except Exception as e:
        return f"Token inválido o error: {e}", 400
