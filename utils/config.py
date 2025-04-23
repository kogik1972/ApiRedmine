## config.apy
import os
from dotenv import load_dotenv

# Carga del .env desde la raíz del proyecto
dotenv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.env'))
load_dotenv(dotenv_path)

# === Entorno ===
ENTORNO = os.getenv("MODO_ENTORNO", "desarrollo").lower()
ES_PRODUCCION = ENTORNO == "produccion"

# === Redmine ===
REDMINE_URL = os.getenv("REDMINE_URL")
API_KEY = os.getenv("REDMINE_API_KEY")

# === Base de datos local (SQLite vía SQLAlchemy) ===
DATABASE_URL = os.getenv("DATABASE_URL")

# === Correo ===
MAIL_SERVER = os.getenv("MAIL_SERVER")
MAIL_PORT = os.getenv("MAIL_PORT")
MAIL_USE_TLS = os.getenv("MAIL_USE_TLS") == "true"
MAIL_USERNAME = os.getenv("MAIL_USERNAME")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER")

# === Redmine DB externa (MySQL) ===
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

# === Flask App Key ===
SECRET_KEY = os.getenv("SECRET_KEY")

# === Dominios ===
FRONT_DOMAIN_LOCAL = os.getenv("FRONT_DOMAIN_LOCAL")
FRONT_DOMAIN_PROD = os.getenv("FRONT_DOMAIN_PROD")

# === Validaciones mínimas obligatorias ===
faltantes = []
if not REDMINE_URL: faltantes.append("REDMINE_URL")
if not API_KEY: faltantes.append("REDMINE_API_KEY")
if not DATABASE_URL: faltantes.append("DATABASE_URL")
if not SECRET_KEY: faltantes.append("SECRET_KEY")

if faltantes:
    raise RuntimeError(f"❌ Variables faltantes en .env: {', '.join(faltantes)}")

# === Log opcional ===
print(f"✅ Configuración cargada. MODO_ENTORNO = {ENTORNO.upper()}")