import os
import sys
sys.path.append(os.path.abspath(os.path.dirname(__file__) + "/.."))  # para encontrar `app`

from app import create_app, db
app = create_app()

with app.app_context():
    print("🧹 Eliminando base si existe...")
    db.drop_all()
    print("📦 Creando base desde cero...")
    db.create_all()
    print("✅ Base de datos lista en:", app.config['SQLALCHEMY_DATABASE_URI'])
