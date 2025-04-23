import os
import json
import mysql.connector
from dotenv import load_dotenv

# Cargar variables desde .env
load_dotenv()

# Directorio y archivo donde se guardará el caché
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = os.path.join(BASE_DIR, "cache")
CACHE_FILE_PATH = os.path.join(CACHE_DIR, "enumeraciones_cache.json")
CUSTOM_VALUES_CACHE_PATH = os.path.join(CACHE_DIR, "custom_values_cache.json")

def ensure_cache_dir_exists():
    """Crea el directorio 'cache/' si no existe."""
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)


def load_enum_cache():
    """Carga el caché desde disco, o devuelve un dict vacío si no existe."""
    ensure_cache_dir_exists()
    if os.path.exists(CACHE_FILE_PATH):
        with open(CACHE_FILE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def load_custom_values_cache():
    ensure_cache_dir_exists()
    if os.path.exists(CUSTOM_VALUES_CACHE_PATH):
        with open(CUSTOM_VALUES_CACHE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_enum_cache(data):
    """Guarda el caché actualizado en disco."""
    with open(CACHE_FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def save_custom_values_cache(data):
    with open(CUSTOM_VALUES_CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_enum_from_db(enum_id):
    """Consulta la base de datos directamente por una enumeración."""
    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM custom_field_enumerations WHERE id = %s", (enum_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row


def get_enum(enum_id, force_reload=False):
    """
    Retorna una enumeración desde el caché local,
    o consulta la base de datos si no está (o si force_reload=True).
    """
    enum_id_str = str(enum_id)
    cache = load_enum_cache()

    if not force_reload and enum_id_str in cache:
        return cache[enum_id_str]

    print(f"🔄 Consultando DB por enumeración ID {enum_id}...")
    data = get_enum_from_db(enum_id)

    if data:
        cache[enum_id_str] = data
        save_enum_cache(cache)

    return data

def get_custom_values_from_db(customized_id, customized_type):
    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT cv.custom_field_id, cf.name AS field_name, cv.value
        FROM custom_values cv
        JOIN custom_fields cf ON cv.custom_field_id = cf.id
        WHERE cv.customized_id = %s AND cv.customized_type = %s
    """
    cursor.execute(query, (customized_id, customized_type))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

def get_custom_values(customized_id, customized_type, force_reload=False):
    """
    Retorna los valores customizados desde caché o desde base de datos si no están en caché.
    """
    key = f"{customized_type}:{customized_id}"
    cache = load_custom_values_cache()

    if not force_reload and key in cache:
        return cache[key]

    print(f"🔄 Consultando DB por custom_values para {key}...")
    data = get_custom_values_from_db(customized_id, customized_type)

    if data:
        cache[key] = data
        save_custom_values_cache(cache)

    return data