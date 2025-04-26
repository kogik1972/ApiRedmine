import os
import sys

# Agregar la raíz del proyecto al sys.path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from redmine.redmine_cierre import cerrar_issue_firma

# Configurar logging básico para test
import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def main():
    # Simular datos de prueba
    issue_id = 4777
    #estado = "firmado"  # Cambiar a "rechazado" para probar rechazo
    estado = "rechazado"  # Cambiar a "rechazado" para probar rechazo

    resultado = cerrar_issue_firma(issue_id, estado)

    if resultado:
        logging.info("Test de redmine_cierre exitoso ✅")
    else:
        logging.error("Test de redmine_cierre fallido ❌")

if __name__ == "__main__":
    main()
