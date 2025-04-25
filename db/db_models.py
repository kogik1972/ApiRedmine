# db/db_models.py

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pytz

db = SQLAlchemy()
santiago_tz = pytz.timezone('America/Santiago')

class Documento(db.Model):
    __tablename__ = 'documentos'

    id = db.Column(db.Integer, primary_key=True)
    issue_id = db.Column(db.Integer, nullable=False)
    nombre_archivo = db.Column(db.String(255), nullable=False)
    ruta_archivo = db.Column(db.String(512), nullable=False)
    estado = db.Column(db.String(50), default='pendiente')
    fecha_creacion = db.Column(db.DateTime, default=lambda: datetime.now(santiago_tz))

    firmantes = db.relationship("Firmante", backref="documento", cascade="all, delete-orphan")
    firmas = db.relationship("FirmaRequerida", backref="documento", cascade="all, delete-orphan")

class Firmante(db.Model):
    __tablename__ = 'firmantes'

    id = db.Column(db.Integer, primary_key=True)
    documento_id = db.Column(db.Integer, db.ForeignKey('documentos.id'), nullable=False)
    nombre = db.Column(db.String(255), nullable=False)
    rut = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    token = db.Column(db.String(255), nullable=False, unique=True)
    aprobado = db.Column(db.Boolean, default=None)
    fecha_respuesta = db.Column(db.DateTime)

    def marcar_aprobado(self):
        self.aprobado = True
        self.fecha_respuesta = datetime.now(santiago_tz)

    def marcar_rechazado(self):
        self.aprobado = False
        self.fecha_respuesta = datetime.now(santiago_tz)

class FirmaRequerida(db.Model):
    __tablename__ = 'firmas_requeridas'

    id = db.Column(db.Integer, primary_key=True)
    documento_id = db.Column(db.Integer, db.ForeignKey('documentos.id'), nullable=False)
    firmante_email = db.Column(db.String(255), nullable=False)
    token = db.Column(db.String(255), nullable=False, unique=True)
    aprobado = db.Column(db.Boolean, default=None)
    fecha_respuesta = db.Column(db.DateTime)

    def registrar_aprobacion(self):
        self.aprobado = True
        self.fecha_respuesta = datetime.now(santiago_tz)

    def registrar_rechazo(self):
        self.aprobado = False
        self.fecha_respuesta = datetime.now(santiago_tz)
