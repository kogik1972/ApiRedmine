# firma/firma_utils.py

import os
from itsdangerous import URLSafeSerializer
from app import db

from utils.logging_config import configurar_logging
import logging
configurar_logging()

# Carga configuración del entorno ya inicializada por Flask
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY no definido en el entorno")

serializer = URLSafeSerializer(SECRET_KEY)

# Detectar dominio según entorno
modo = os.getenv("MODO_ENTORNO", "desarrollo").lower()
if modo == "produccion":
    base_url = os.getenv("FRONT_DOMAIN_PROD", "https://condominium.eproc-chile.cl")
else:
    base_url = os.getenv("FRONT_DOMAIN_LOCAL", "http://127.0.0.1:5003")


def crear_link_firma(token, accion):
    if accion not in ("aceptar", "rechazar"):
        raise ValueError("Acción inválida para link de firma")
    return f"{base_url}/firmar?token={token}&accion={accion}"


def registrar_firmante(documento_id, nombre, rut, email, tipo):
    from db.db_models import FirmaRequerida

    firma_uuid = str(uuid.uuid4())
    token_aceptar = serializer.dumps({"firma_uuid": firma_uuid, "accion": "aceptar"})
    token_rechazar = serializer.dumps({"firma_uuid": firma_uuid, "accion": "rechazar"})

    firma = FirmaRequerida(
        documento_id=documento_id,
        nombre=nombre,
        rut=rut,
        email=email,
        tipo=tipo,
        estado='pendiente',
        token = token_aceptar  
    )
    db.session.add(firma)
    db.session.commit()  # ⚡ OJO: flush() para obtener firma.id SIN commitear aún

    token_aceptar = serializer.dumps({"firma_id": firma.id, "accion": "aceptar"})
    token_rechazar = serializer.dumps({"firma_id": firma.id, "accion": "rechazar"})

    return {
        "firma": firma,
        "link_aceptar": crear_link_firma(token_aceptar, "aceptar"),
        "link_rechazar": crear_link_firma(token_rechazar, "rechazar"),
    }
