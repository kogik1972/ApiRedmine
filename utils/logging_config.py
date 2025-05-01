import logging
import os

def configurar_logging():
    # Obtener raíz absoluta del proyecto
    ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    log_file_path = os.path.join(ROOT_DIR, "firma.log")

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file_path),
            logging.StreamHandler()
        ]
    )
