# scripts/genera_token.py

import os
from dotenv import load_dotenv
from itsdangerous import URLSafeSerializer

from utils.logging_config import configurar_logging
import logging
configurar_logging()

load_dotenv()

# Detectar entorno actual
modo = os.getenv("MODO_ENTORNO", "desarrollo").lower()
if modo == "produccion":
    dominio = os.getenv("FRONT_DOMAIN_PROD", "https://condominium.eproc-chile.cl")
else:
    dominio = os.getenv("FRONT_DOMAIN_LOCAL", "http://127.0.0.1:5003")

SECRET_KEY = os.getenv("SECRET_KEY")
serializer = URLSafeSerializer(SECRET_KEY)

# Solicita firma_id
try:
    firma_id = int(input("🔢 Ingresa el firma_id existente en la BD: ").strip())
except ValueError:
    logging.info(f"genera_token.py - Debes ingresar un número entero válido.")
    exit(1)

# Generar tokens
token_aceptar = serializer.dumps({"firma_id": firma_id, "accion": "aceptar"})
token_rechazar = serializer.dumps({"firma_id": firma_id, "accion": "rechazar"})

# Imprimir enlaces correctos (con parámetros tipo query)
logging.info(f"genera_token.py - Enlace para aceptar:")
logging.info(f"genera_token.py - {dominio}/firmar?token={token_aceptar}&accion=aceptar")

logging.info(f"genera_token.py - Enlace para rechazar:")
logging.info(f"genera_token.py - {dominio}/firmar?token={token_rechazar}&accion=rechazar")
