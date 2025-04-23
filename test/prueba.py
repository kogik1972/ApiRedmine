# test/prueba.py
import sys
import os
from redmine.redmine_client import obtener_emails_desde_redmine

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)



issue_id = input("Id? ")
resultado = obtener_emails_desde_redmine(issue_id)