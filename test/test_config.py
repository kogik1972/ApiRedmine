import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.config import (
    REDMINE_URL, REDMINE_API_KEY, DATABASE_URL,
    MAIL_SERVER, MAIL_USERNAME, FRONT_DOMAIN_LOCAL, FRONT_DOMAIN_PROD,
    SECRET_KEY, ENTORNO, ES_PRODUCCION
)

def mostrar_config():
    print("\n🔍 CONFIGURACIÓN ACTUAL CARGADA\n")

    print(f"🧭 ENTORNO: {ENTORNO.upper()} {'(Producción)' if ES_PRODUCCION else '(Desarrollo)'}")
    print(f"🔑 REDMINE_URL: {REDMINE_URL}")
    print(f"🔑 REDMINE_API_KEY: {REDMINE_API_KEY[:5]}...{REDMINE_API_KEY[-5:]}")
    print(f"🗃 DATABASE_URL: {DATABASE_URL}")
    print(f"✉️ MAIL_SERVER: {MAIL_SERVER}")
    print(f"✉️ MAIL_USERNAME: {MAIL_USERNAME}")
    print(f"🌐 DOMINIO LOCAL: {FRONT_DOMAIN_LOCAL}")
    print(f"🌐 DOMINIO PRODUCCIÓN: {FRONT_DOMAIN_PROD}")
    print(f"🔒 SECRET_KEY: {SECRET_KEY[:8]}...")

    print("\n✅ Todas las variables principales están cargadas correctamente.\n")

if __name__ == "__main__":
    mostrar_config()
