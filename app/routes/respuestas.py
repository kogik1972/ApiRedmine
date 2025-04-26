from flask import Blueprint, render_template, request
from app import db
from db.db_models import FirmaRequerida
from itsdangerous import URLSafeSerializer
from datetime import datetime, timezone
from dotenv import load_dotenv
import os
import traceback
import pytz

# Cargar variables de entorno
load_dotenv()

# Blueprint
respuestas_bp = Blueprint('respuestas', __name__)

# Serializador
SECRET_KEY = os.getenv("SECRET_KEY")
serializer = URLSafeSerializer(SECRET_KEY)

# 🔵 Importar funciones de estampado, envío y cierre
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

        # Preparar datos
        issue_id = documento.issue_id
        nombre_documento = documento.nombre
        path_documento = documento.path_pdf
        firmas_requeridas = [f for f in documento.firmas]  # Ajustar según estructura
        destinatarios = [f.email for f in documento.firmas]  # Ajustar si los destinatarios son otros

        print(f"respuestas.py issue_id:{issue_id}")
        print(f"respuestas.py nombre_documento:{nombre_documento}")
        print(f"respuestas.py path_documento:{path_documento}")

        if "rechazado" in estados:
            documento.estado_firma = "rechazado"
            #3) Cerrar issue en Redmine
            resultado_cierre = cerrar_issue_firma(issue_id, "rechazado")
            if not resultado_cierre:
                raise Exception("Error al rechazar issue en Redmine")
        elif all(e == "aceptado" for e in estados):
            documento.estado_firma = "firmado"
            # 1) Estampar firmas
            resultado_estampado = estampar_firmas(issue_id, nombre_documento, path_documento, firmas_requeridas)
            if not resultado_estampado:
                raise Exception("Error al estampar firmas")

            # 2) Enviar documento firmado
            resultado_envio = enviar_documento_firmado(issue_id, path_documento, nombre_documento, destinatarios)
            if not resultado_envio:
                raise Exception("Error al enviar documento firmado")

            # 3) Cerrar issue en Redmine
            resultado_cierre = cerrar_issue_firma(issue_id, "firmado")
            if not resultado_cierre:
                raise Exception("Error al cerrar issue en Redmine")

        db.session.commit()

        return render_template("gracias.html", estado=firma.estado)

    except Exception as e:
        return f"<pre>{traceback.format_exc()}</pre>", 500
