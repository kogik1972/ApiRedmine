import re

def parsear_enumeracion(texto):
    match = re.match(r'^(?P<nombre>.+?) - (?P<rut>[\d\.]+-[\dkK]) - (?P<id>\d+)$', texto)
    return match.groupdict() if match else None
