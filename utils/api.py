## utils/api.py
import requests
import logging
from utils.config import REDMINE_URL, API_KEY as REDMINE_API_KEY

def get_json(path):
    """
    Hace un GET a la API de Redmine y retorna el JSON como dict.
    Lanza excepción o retorna None si falla.
    """
    if not REDMINE_URL or not REDMINE_API_KEY:
        raise RuntimeError("REDMINE_URL o REDMINE_API_KEY no están definidos en utils/config.py")

    headers = { "X-Redmine-API-Key": REDMINE_API_KEY }
    url = f"{REDMINE_URL.rstrip('/')}/{path.lstrip('/')}"
    logging.info(f"api - GET request a Redmine: {url}")

    try:
        resp = requests.get(url, headers=headers)
        resp.raise_for_status()
        logging.info(f"api - ✅ Respuesta exitosa: {resp.status_code} {url}")
        return resp.json()

    except requests.HTTPError as e:
        logging.error(f"api - ❌ HTTP error {e.response.status_code} en {url}: {e.response.reason}")
    except requests.RequestException as e:
        logging.error(f"api - ❌ Error de conexión o red al acceder a {url}: {e}")
    except Exception as e:
        logging.error(f"api - ❌ Excepción inesperada al consultar {url}: {e}")

    return None
