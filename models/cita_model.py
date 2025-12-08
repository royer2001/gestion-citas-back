from extensions.database import db
from datetime import datetime

class Cita(db.Model):
    __tablename__ = "citas"

    id = db.Column(db.Integer, primary_key=True)
    paciente_id = db.Column(db.Integer, db.ForeignKey('pacientes.id'), nullable=False)
    horario_id = db.Column(db.Integer, db.ForeignKey('horarios_medicos.id'), nullable=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True)
    area_id = db.Column(db.Integer, db.ForeignKey('areas.id'), nullable=True)
    area = db.Column(db.String(100), nullable=True)  # Mantener para compatibilidad
    fecha = db.Column(db.Date, nullable=True)  # Fecha de la cita
    sintomas = db.Column(db.Text, nullable=False)
    
    # Datos del acompañante
    dni_acompanante = db.Column(db.String(8))
    nombre_acompanante = db.Column(db.String(150))
    telefono_acompanante = db.Column(db.String(15))
    
    datos_adicionales = db.Column(db.JSON)

    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    estado = db.Column(db.String(20), default="pendiente")

    # Relaciones
    paciente = db.relationship('Paciente', backref=db.backref('citas', lazy=True))
    horario = db.relationship('HorarioMedico', backref=db.backref('citas', lazy=True))
    doctor = db.relationship('Usuario', backref=db.backref('citas_asignadas', lazy=True))
    area_rel = db.relationship('Area', backref=db.backref('citas', lazy=True))

    def to_dict(self):
        return {
            "id": self.id,
            "paciente_id": self.paciente_id,
            "horario_id": self.horario_id,
            "doctor_id": self.doctor_id,
            "area_id": self.area_id,
            "area": self.area or (self.area_rel.nombre if self.area_rel else None),
            "fecha": str(self.fecha) if self.fecha else None,
            "sintomas": self.sintomas,
            "dni_acompanante": self.dni_acompanante,
            "nombre_acompanante": self.nombre_acompanante,
            "telefono_acompanante": self.telefono_acompanante,
            "datos_adicionales": self.datos_adicionales,
            "fecha_registro": str(self.fecha_registro),
            "estado": self.estado,
            # Datos adicionales de relaciones
            "doctor_nombre": self.doctor.nombres_completos if self.doctor else None,
            "area_nombre": self.area_rel.nombre if self.area_rel else self.area,
            "horario_turno": self.horario.turno if self.horario else None,
            "horario_turno_nombre": self.horario.turno_nombre if self.horario else None,
        }
