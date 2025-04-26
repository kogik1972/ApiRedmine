from dotenv import load_dotenv
load_dotenv()

import os
import sys
import platform

sistema = platform.system()

if sistema == "Windows":
    base_dir = os.path.join("D:/", "redmine-5.1.3", "files", "2025", "04")
elif sistema == "Linux":
    base_dir = os.path.join("/home", "desa", "Data", "redmine-5.1.3", "files", "2025", "04")
else:
    raise Exception("Sistema operativo no soportado")

# Agregar la raíz del proyecto al sys.path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import logging
from firma.firma_cierre import enviar_documento_firmado

# Configurar logging básico para test
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def main():
    # Simular datos de prueba
    issue_id = 4775
    documento_path = base_dir
    documento_nombre = "4.477.432-1_20250424_205215_AnexoCambioSueldo.docx"

    destinatarios = [
        {"nombre": "Juan Pablo Alvarez", "email": "jp.alvarez.o@gmail.com"},
        {"nombre": "Angie Godoy Nelson", "email": "juan.pablo@eproc-chile.cl"}
    ]

    resultado = enviar_documento_firmado(
        issue_id,
        documento_path,
        documento_nombre,
        destinatarios
    )
    
    if resultado:
        logging.info("Test de firma_cierre exitoso ✅")
    else:
        logging.error("Test de firma_cierre fallido ❌")

if __name__ == "__main__":
    main()
