## validar.py
from flask import Blueprint, render_template, request
from app import db
from db.db_models import Documento
import logging

from utils.logging_config import configurar_logging
configurar_logging()
logger = logging.getLogger(__name__)

validar_bp = Blueprint('validar', __name__)

@validar_bp.route("/validar", methods=["GET", "POST"], strict_slashes=False)
def validar_documento():
    if request.method == "POST":
        token = request.form.get("token")

        if not token:
            return render_template("validar.html", error="Debe ingresar un código para validar.")

        logger.info(f"validar.py - Buscando documento con token {token}")
        documento = Documento.query.filter_by(token_documento=token).first()

        if not documento:
            return render_template("validar.html", error="Código no válido o documento no encontrado.")

        return render_template("validado.html", documento=documento, firmas=documento.firmas)

    return render_template("validar.html")
