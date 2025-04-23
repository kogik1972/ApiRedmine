## api.py
import requests
from utils.config import REDMINE_URL, API_KEY as REDMINE_API_KEY

def get_json(path):
    """
    Hace un GET a la API de Redmine y retorna el JSON como dict.
    Lanza excepción o retorna None si falla.
    """
    headers = { "X-Redmine-API-Key": REDMINE_API_KEY }
    url = f"{REDMINE_URL.rstrip('/')}/{path.lstrip('/')}"

    try:
        resp = requests.get(url, headers=headers)
        resp.raise_for_status()
        return resp.json()
    
    except requests.HTTPError as e:
        print(f"[GET {url}] Error HTTP {e.response.status_code}: {e.response.reason}")
    except requests.RequestException as e:
        print(f"[GET {url}] Error de red o conexión: {e}")
    except Exception as e:
        print(f"[GET {url}] Excepción inesperada: {e}")

    return None
