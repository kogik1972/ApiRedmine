import sys
import os

# Agregar la raíz del proyecto al sys.path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import platform
import logging
from firma.estampar_firmas import estampar_firmas

# Configurar logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def main():
    issue_id = 4775
    nombre_documento = "4.477.432-1_20250424_205215_AnexoCambioSueldo.docx"

    # Detectar sistema operativo
    sistema = platform.system()

    if sistema == "Windows":
        base_dir = os.path.join("D:\\", "redmine-5.1.3", "files", "2025", "04")
    elif sistema == "Linux":
        base_dir = os.path.join("/home", "desa", "Data", "redmine-5.1.3", "files", "2025", "04")
    else:
        logging.error(f"Sistema operativo no soportado: {sistema}")
        return

    path_documento = base_dir

    firmas_requeridas = [
        {"nombre": "Juan Pablo Alvarez", "rut": "12.262.608-3", "fecha_firma": "25-04-2025 01:25", "tipo": "firmante"},
        {"nombre": "Angie Godoy Nelson", "rut": "12.249.408-K", "fecha_firma": "25-04-2025 09:30", "tipo": "responsable"}
    ]

    resultado = estampar_firmas(issue_id, nombre_documento, path_documento, firmas_requeridas)

    if resultado:
        logging.info("Test de estampado exitoso ✅")
    else:
        logging.error("Test de estampado fallido ❌")

if __name__ == "__main__":
    main()