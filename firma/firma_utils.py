# firma/firma_utils.py

import os
import uuid
from db.db_models import db, FirmaRequerida

def crear_link_firma(token, accion):
    
    base_url = os.getenv("BASE_URL_FIRMA", "https://condominium.eproc-chile.cl")
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
