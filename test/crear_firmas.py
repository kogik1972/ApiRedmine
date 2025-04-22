# scripts/crear_firma_dummy.py
import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__) + "/.."))

from dotenv import load_dotenv
from datetime import datetime
import uuid

from app import create_app, db
from db.db_models import Documento, FirmaRequerida

load_dotenv()
app = create_app()

with app.app_context():
    # Crear documento de prueba
    doc = Documento(
        nombre="Documento de prueba listener",
        path_pdf="docs/contrato_prueba.pdf",
        fecha_generacion=datetime.now()
    )
    db.session.add(doc)
    db.session.commit()

    # Crear firmante de prueba
    token = str(uuid.uuid4())
    firma = FirmaRequerida(
        documento_id=doc.id,
        nombre="Juan Firmante Listener",
        rut="1.234.567-8",
        email="juan@example.com",
        token=token,
        tipo="firmante",
        estado="pendiente"
    )
    db.session.add(firma)
    db.session.commit()

    print("🎉 Firma dummy creada con éxito")
    print(f"🆔 ID: {firma.id}")
    print(f"🔐 Token: {firma.token}")
