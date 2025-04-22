# scripts/genera_token.py

import os
from dotenv import load_dotenv
from itsdangerous import URLSafeSerializer

load_dotenv()
modo = os.getenv("MODO_ENTORNO", "desarrollo")  # 👈 detecta entorno actual
if modo == "produccion":
    dominio = os.getenv("FRONT_DOMAIN_PROD", "https://condominium.eproc-chile.cl")
else:
    dominio = os.getenv("FRONT_DOMAIN_LOCAL", "http://127.0.0.1:5000")

SECRET_KEY = os.getenv("SECRET_KEY")
DOMINIO = dominio
#DOMINIO = "http://127.0.0.1:5000"  # Cambia si vas a testear en producción

serializer = URLSafeSerializer(SECRET_KEY)

# Cambia estos valores según el registro que ya exista en tu BD
firma_id = 4741
accion_aceptar = "aceptar"
accion_rechazar = "rechazar"

token_aceptar = serializer.dumps({"firma_id": firma_id, "accion": accion_aceptar})
token_rechazar = serializer.dumps({"firma_id": firma_id, "accion": accion_rechazar})

print("🔗 Enlace para aceptar:")
print(f"{DOMINIO}/respuesta_firma/{token_aceptar}")

print("\n🔗 Enlace para rechazar:")
print(f"{DOMINIO}/respuesta_firma/{token_rechazar}")
