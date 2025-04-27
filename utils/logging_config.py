import logging

def configurar_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        handlers=[
            logging.FileHandler("firma.log", encoding="utf-8"),
            logging.StreamHandler()
        ]
    )
