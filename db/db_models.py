from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Documento(db.Model):
    __tablename__ = 'documentos'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), nullable=False)
    path_pdf = db.Column(db.String(512), nullable=False)
    fecha_generacion = db.Column(db.DateTime, default=datetime.utcnow)
    estado_firma = db.Column(db.String(20), default='pendiente')  # pendiente, firmado, rechazado

    firmas = db.relationship('FirmaRequerida', backref='documento', lazy=True)

    def __repr__(self):
        return f"<Documento {self.id} - {self.nombre}>"


class FirmaRequerida(db.Model):
    __tablename__ = 'firmas_requeridas'

    id = db.Column(db.Integer, primary_key=True)
    documento_id = db.Column(db.Integer, db.ForeignKey('documentos.id'), nullable=False)
    nombre = db.Column(db.String(255), nullable=False)
    rut = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    token = db.Column(db.String(255), unique=True, nullable=False)
    estado = db.Column(db.String(20), default='pendiente')  # pendiente, aceptada, rechazada
    fecha_firma = db.Column(db.DateTime, nullable=True)
    tipo = db.Column(db.String(20), nullable=True)  # responsable o firmante

    def __repr__(self):
        return f"<Firma {self.nombre} ({self.tipo}) - {self.estado}>"
