from extensions.database import db
from datetime import time, date

class HorarioMedico(db.Model):
    __tablename__ = "horarios_medicos"

    id = db.Column(db.Integer, primary_key=True)
    medico_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    area_id = db.Column(db.Integer, db.ForeignKey('areas.id'), nullable=False)
    
    # Fecha específica del horario (para gestión mensual)
    fecha = db.Column(db.Date, nullable=False)
    
    # 0=Lunes, 1=Martes, ..., 6=Domingo (se calcula de la fecha pero se mantiene para filtros rápidos)
    dia_semana = db.Column(db.Integer, nullable=False) 
    
    # Turno: 'M' = Mañana (07:30-13:30), 'T' = Tarde (13:30-19:30)
    turno = db.Column(db.String(1), nullable=False, default='M')
    
    # Cupos para este turno específico
    cupos = db.Column(db.Integer, nullable=False, default=0)
    
    # Constraint único: un médico solo puede tener un horario por fecha y turno
    __table_args__ = (
        db.UniqueConstraint('medico_id', 'fecha', 'turno', name='unique_medico_fecha_turno'),
    )

    medico = db.relationship('Usuario', backref=db.backref('horarios', lazy=True))
    area = db.relationship('Area', backref=db.backref('horarios', lazy=True))

    # Constantes de horario
    HORARIO_MANANA_INICIO = time(7, 30)
    HORARIO_MANANA_FIN = time(13, 30)
    HORARIO_TARDE_INICIO = time(13, 30)
    HORARIO_TARDE_FIN = time(19, 30)

    @property
    def hora_inicio(self):
        """Retorna la hora de inicio según el turno"""
        return self.HORARIO_MANANA_INICIO if self.turno == 'M' else self.HORARIO_TARDE_INICIO

    @property
    def hora_fin(self):
        """Retorna la hora de fin según el turno"""
        return self.HORARIO_MANANA_FIN if self.turno == 'M' else self.HORARIO_TARDE_FIN

    @property
    def turno_nombre(self):
        """Retorna el nombre del turno"""
        return "Mañana" if self.turno == 'M' else "Tarde"

    def to_dict(self):
        return {
            "id": self.id,
            "medico_id": self.medico_id,
            "area_id": self.area_id,
            "fecha": str(self.fecha) if self.fecha else None,
            "dia_semana": self.dia_semana,
            "turno": self.turno,
            "turno_nombre": self.turno_nombre,
            "hora_inicio": str(self.hora_inicio),
            "hora_fin": str(self.hora_fin),
            "cupos": self.cupos,
            "medico_nombre": self.medico.nombres_completos if self.medico and self.medico.nombres_completos else (self.medico.username if self.medico else None),
            "area_nombre": self.area.nombre if self.area else None
        }
