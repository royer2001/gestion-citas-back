from extensions.database import db
from datetime import datetime

class Cita(db.Model):
    __tablename__ = "citas"

    id = db.Column(db.Integer, primary_key=True)
    paciente_id = db.Column(db.Integer, db.ForeignKey('pacientes.id'), nullable=False)
    doctor_id = db.Column(db.Integer, nullable=True)
    area = db.Column(db.String(100), nullable=False)
    sintomas = db.Column(db.Text, nullable=False)
    
    # Datos del acompañante
    dni_acompanante = db.Column(db.String(8))
    nombre_acompanante = db.Column(db.String(150))
    telefono_acompanante = db.Column(db.String(15))
    
    datos_adicionales = db.Column(db.JSON)

    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    estado = db.Column(db.String(20), default="pendiente")

    paciente = db.relationship('Paciente', backref=db.backref('citas', lazy=True))

    def to_dict(self):
        return {
            "id": self.id,
            "paciente_id": self.paciente_id,
            "doctor_id": self.doctor_id,
            "area": self.area,
            "sintomas": self.sintomas,
            "dni_acompanante": self.dni_acompanante,
            "nombre_acompanante": self.nombre_acompanante,
            "telefono_acompanante": self.telefono_acompanante,
            "datos_adicionales": self.datos_adicionales,
            "fecha_registro": str(self.fecha_registro),
            "estado": self.estado
        }
