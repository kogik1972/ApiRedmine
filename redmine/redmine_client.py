# redmine_client.py
import sys
import os

# Asegura que la raíz del proyecto esté en el path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import requests

from dotenv import load_dotenv
#from redmine.redmine_fields import get_custom_field_by_name
from redmine.redmine_cache_sql import get_enum, get_custom_values
from utils.api import get_json
from utils.parser import parsear_enumeracion

load_dotenv()
REDMINE_URL = os.getenv("REDMINE_URL")
REDMINE_API_KEY = os.getenv("REDMINE_API_KEY")

trab_email = 'trab_email'
email_responsable = None 
email_trabajador = None

def obtener_emails_desde_redmine(issue_id):
    try:
        # 1. Obtener informacion del issue
        issue_json = get_json(f"issues/{issue_id}.json")
        if issue_json:
            issue_data = issue_json["issue"]
            campos_issue = issue_data["custom_fields"]
            campos_dict_issue = {campo["name"]: campo["value"] for campo in campos_issue}
            
            id_proyecto = issue_data["project"]["id"]
            #print(f"redmine_client.obtener_emails_desde_redmine - id_proyecto: {id_proyecto}")

            # 2. Obtener información proyecto padre
            proyecto_data = get_json(f"projects/{id_proyecto}.json")["project"]
            id_proyecto_padre = proyecto_data.get("parent", {}).get("id")
            #print(f"redmine_client.obtener_emails_desde_redmine - id_proyecto_padre: {id_proyecto_padre}")

            # 3. Obtener información email_responsable
            data = get_json(f"projects/{id_proyecto_padre}.json?include=custom_fields")
            campos = data["project"]["custom_fields"]
            campos_dict = {campo["name"]: campo["value"] for campo in campos}
            email_responsable = campos_dict.get("eMail_Administrador")
            rut_responsable = campos_dict.get("RUT_Rep_Legal_Administrador")
            nombre_responsable = campos_dict.get("Nombre_Rep_Legal_Administrador")


            # 4. Obtener nombre comunidad
            data = get_json(f"projects/{id_proyecto}.json?include=custom_fields")
            campos = data["project"]["custom_fields"]
            campos_dict = {campo["name"]: campo["value"] for campo in campos}
            nombre_comunidad = (f"RUT_{campos_dict.get('Comunidad')}")
            #print(f"nombre_comunidad:{nombre_comunidad}")

            #campo_cf = get_custom_field_by_name(nombre_comunidad)
            #print(f"id_cf: {campo_cf["id"]}")

            id_enum = campos_dict_issue.get(nombre_comunidad)
            #print(f"id_enum: {id_enum}")

            if id_enum:
                enum = get_enum(id_enum)
                #print(f"Enumeración: {enum}")
        
                if enum:
                    texto_enumeracion = enum['name']
                    resultado = parsear_enumeracion(texto_enumeracion)

                    if resultado:
                        nombre_firmante = resultado['nombre']
                        rut_firmante = resultado['rut']
                        id_original = resultado['id']

                        #campo_cf = get_custom_field_by_name(trab_email)
                        #print(f"id_cf trab_email: {campo_cf["id"]}")

                        campos = get_custom_values(id_original, "Issue")
                        for campo in campos:
                            if campo['field_name'] == trab_email:
                                email_firmante = campo['value']
                                break

                        print("**********************************************")
                        print(f"email_responsable: {email_responsable}")
                        print(f"rut_responsable: {rut_responsable}")
                        print(f"nombre_responsable: {nombre_responsable}")
                        print("---------------------------------------------")
                        print(f"email_firmante: {email_firmante}")
                        print(f"rut_firmante: {rut_firmante}")
                        print(f"nombre_firmante: {nombre_firmante}")
                        print("**********************************************")

            return {
                "responsable": {
                    "nombre": nombre_responsable,
                    "rut": rut_responsable,
                    "email": email_responsable
                },
                "firmante": {
                    "nombre": nombre_firmante,
                    "rut": rut_firmante,
                    "email": email_firmante
                }

            }
        
        else:
            print("ERROR")        
    except requests.RequestException as e:
        print(f"❌ Error al consultar Redmine: {e}")
        return None, None