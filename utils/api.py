# api.py

import os
import requests
from dotenv import load_dotenv

load_dotenv()
REDMINE_URL = os.getenv("REDMINE_URL")
REDMINE_API_KEY = os.getenv("REDMINE_API_KEY")

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
