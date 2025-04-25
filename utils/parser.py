## utils/parser.py
import re
import logging

def parsear_enumeracion(texto):
    logging.info(f"parser - Intentando parsear enumeración: '{texto}'")
    match = re.match(r'^(?P<nombre>.+?) - (?P<rut>[\d\.]+-[\dkK]) - (?P<id>\d+)$', texto)
    if match:
        resultado = match.groupdict()
        logging.info(f"parser - ✅ Parseo exitoso: {resultado}")
        return resultado
    else:
        logging.warning(f"parser - ❌ No se pudo parsear el texto: '{texto}'")
        return None
