# db/db_init.py

import os
import sys
from datetime import datetime
import pytz

# Agrega el directorio raíz al path para que se pueda importar `app`
sys.path.append(os.path.abspath(os.path.dirname(__file__) + "/.."))

from app import create_app, db
from db.db_models import Documento, Firmante

# Configura zona horaria de Santiago
santiago_tz = pytz.timezone('America/Santiago')

# Crea la app
app = create_app()

if app.config.get("ENV") != "production":
    with app.app_context():
        print("🧹 Eliminando base si existe...")
        db.drop_all()

        print("📦 Creando base desde cero...")
        db.create_all()

        print("✅ Base de datos lista en:", app.config['SQLALCHEMY_DATABASE_URI'])

        # Inserta un documento de prueba
        doc = Documento(
            issue_id=9999,
            nombre_archivo="prueba_inicial.pdf",
            ruta_archivo="docs/prueba_inicial.pdf",
            estado="pendiente",
            fecha_creacion=datetime.now(santiago_tz)
        )
        db.session.add(doc)
        db.session.commit()

        # Inserta un firmante asociado
        firmante = Firmante(
            documento_id=doc.id,
            nombre="Firmante Prueba",
            rut="11.111.111-1",
            email="firmante@correo.cl",
            token="TOKEN-DE-EJEMPLO-123",
            aprobado=None
        )
        db.session.add(firmante)
        db.session.commit()

        print("🧪 Datos de prueba insertados correctamente.")
else:
    print("⚠️ Esta operación no está permitida en entorno de producción.")
