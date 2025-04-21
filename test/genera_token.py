# test/genera_token.py

from itsdangerous import URLSafeSerializer
import os
from dotenv import load_dotenv

# Carga las variables del entorno desde .env
load_dotenv()

# Leer la clave secreta desde el entorno
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    print("❌ ERROR: SECRET_KEY no está definida en el .env")
    exit(1)

# Crear el serializador
serializer = URLSafeSerializer(SECRET_KEY)

# Solicita el ID de la firma al usuario
try:
    firma_id = int(input("Ingrese el ID de la firma (firma_id): "))
except ValueError:
    print("❌ ERROR: El ID debe ser un número entero.")
    exit(1)

# Generar tokens
token_aceptar = serializer.dumps({"firma_id": firma_id, "accion": "aceptar"})
token_rechazar = serializer.dumps({"firma_id": firma_id, "accion": "rechazar"})

# URL base del sistema
BASE_URL = "https://condominium.eproc-chile.cl/respuesta_firma"

print("\n✅ Link para aceptar:")
print(f"{BASE_URL}/{token_aceptar}")

print("\n❌ Link para rechazar:")
print(f"{BASE_URL}/{token_rechazar}")
