# firma/firma_utils.py

import os
import uuid
from app import db                          # ✅ Instancia oficial de SQLAlchemy
from db.db_models import FirmaRequerida     # ✅ Modelo definido en el módulo correcto
from dotenv import load_dotenv
load_dotenv()
modo = os.getenv("MODO_ENTORNO", "desarrollo")  # 👈 detecta entorno actual
if modo == "produccion":
    base_url = os.getenv("FRONT_DOMAIN_PROD", "https://condominium.eproc-chile.cl")
else:
    base_url = os.getenv("FRONT_DOMAIN_LOCAL", "http://127.0.0.1:5000")

def crear_link_firma(token, accion):
    
    if accion not in ("acepta", "rechaza"):
        raise ValueError("Acción inválida para link de firma")

    return f"{base_url}/firmar?token={token}&accion={accion}"


def registrar_firmante(documento_id, nombre, rut, email, tipo):
    """
    Registra un firmante en la base de datos con token único.

    Args:
        documento_id (int): ID del documento.
        nombre (str): Nombre del firmante.
        rut (str): RUT del firmante.
        email (str): Email del firmante.
        tipo (str): Tipo de firmante ('firmante' o 'responsable').

    Returns:
        str: Token generado para el firmante.
    """
    token = str(uuid.uuid4())

    firma = FirmaRequerida(
        documento_id=documento_id,
        nombre=nombre,
        rut=rut,
        email=email,
        token=token,
        tipo=tipo
    )

    db.session.add(firma)
    db.session.commit()

    return token
