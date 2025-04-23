# firma/firma_utils.py

import os
from dotenv import load_dotenv
from itsdangerous import URLSafeSerializer
from app import db

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
serializer = URLSafeSerializer(SECRET_KEY)

# Detectar dominio según entorno
modo = os.getenv("MODO_ENTORNO", "desarrollo").lower()
if modo == "produccion":
    base_url = os.getenv("FRONT_DOMAIN_PROD", "https://condominium.eproc-chile.cl")
else:
    base_url = os.getenv("FRONT_DOMAIN_LOCAL", "http://127.0.0.1:5000")

def crear_link_firma(token, accion):
    if accion not in ("aceptar", "rechazar"):
        raise ValueError("Acción inválida para link de firma")
    return f"{base_url}/firmar?token={token}&accion={accion}"

def registrar_firmante(documento_id, nombre, rut, email, tipo, issue_id):
    from db.db_models import FirmaRequerida

    firma = FirmaRequerida(
        documento_id=documento_id,
        issue_id,
        nombre=nombre,
        rut=rut,
        email=email,
        tipo=tipo,
        estado='pendiente',
        token = 'relleno'
    )
    db.session.add(firma)
    db.session.commit()

    # Token 
    token_aceptar = serializer.dumps({"firma_id": firma.id, "accion": "aceptar"})
    token_rechazar = serializer.dumps({"firma_id": firma.id, "accion": "rechazar"})

    # Asignamos token real
    firma.token = token_aceptar
    db.session.commit()

    # Devolver ambos enlaces para usar en el correo
    return {
        "firma": firma,
        "link_aceptar": crear_link_firma(token_aceptar, "aceptar"),
        "link_rechazar": crear_link_firma(token_rechazar, "rechazar"),
    }
