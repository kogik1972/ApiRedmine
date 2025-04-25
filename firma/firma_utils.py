# firma/firma_utils.py
import os
import logging
from itsdangerous import URLSafeSerializer
from app import db

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
    link = f"{base_url}/firmar?token={token}&accion={accion}"
    logging.info(f"firma_utils - Link generado ({accion}): {link}")
    return link

def registrar_firmante(documento_id, nombre, rut, email, tipo):
    from db.db_models import FirmaRequerida

    logging.info(f"firma_utils - Registrando firmante: {nombre} ({email}) tipo: {tipo}")

    firma = FirmaRequerida(
        documento_id=documento_id,
        nombre=nombre,
        rut=rut,
        email=email,
        tipo=tipo,
        estado='pendiente',
        token='relleno'
    )
    db.session.add(firma)
    db.session.commit()  # Para obtener firma.id

    token_aceptar = serializer.dumps({"firma_id": firma.id, "accion": "aceptar"})
    token_rechazar = serializer.dumps({"firma_id": firma.id, "accion": "rechazar"})

    firma.token = token_aceptar
    db.session.commit()

    logging.info(f"firma_utils - Token generado para firma ID {firma.id}")
    return {
        "firma": firma,
        "link_aceptar": crear_link_firma(token_aceptar, "aceptar"),
        "link_rechazar": crear_link_firma(token_rechazar, "rechazar"),
    }
