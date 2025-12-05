from extensions.database import db
from datetime import datetime

class Paciente(db.Model):
    __tablename__ = "pacientes"

    id = db.Column(db.Integer, primary_key=True)
    dni = db.Column(db.String(8), unique=True, nullable=False)
    nombres = db.Column(db.String(100), nullable=False)
    apellido_paterno = db.Column(db.String(100), nullable=False)
    apellido_materno = db.Column(db.String(100), nullable=False)
    fecha_nacimiento = db.Column(db.Date, nullable=False)
    sexo = db.Column(db.String(1), nullable=False)
    estado_civil = db.Column(db.String(1), nullable=False)
    grado_instruccion = db.Column(db.Enum(
        'inicial_incompleta', 'inicial_completa', 
        'primaria_incompleta', 'primaria_completa', 
        'secundaria_incompleta', 'secundaria_completa', 
        'tecnico_superior_incompleta', 'tecnico_superior_completa', 
        'universitario_incompleto', 'universitario_completo',
        name='grado_instruccion_enum'
    ))

    religion = db.Column(db.String(50))
    procedencia = db.Column(db.String(50))
    telefono = db.Column(db.String(15))
    email = db.Column(db.String(120))
    direccion = db.Column(db.Text, nullable=False)

    # dni_acompanante removed as it belongs to Cita
    # nombre_acompanante removed as it belongs to Cita
    # telefono_acompanante removed as it belongs to Cita

    # sintomas removed as it belongs to Cita
    seguro = db.Column(db.String(50))
    # datos_adicionales removed as it belongs to Cita

    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        # Calcular edad
        today = datetime.now().date()
        age = today.year - self.fecha_nacimiento.year - ((today.month, today.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day))

        return {
            "id": self.id,
            "dni": self.dni,
            "nombres": self.nombres,
            "apellido_paterno": self.apellido_paterno,
            "apellidoPaterno": self.apellido_paterno, # Frontend compatibility
            "apellido_materno": self.apellido_materno,
            "apellidoMaterno": self.apellido_materno, # Frontend compatibility
            "fecha_nacimiento": str(self.fecha_nacimiento),
            "fechaNacimiento": str(self.fecha_nacimiento), # Frontend compatibility
            "edad": age, # Frontend requirement
            "sexo": self.sexo,
            "estado_civil": self.estado_civil,
            "grado_instruccion": self.grado_instruccion,
            "religion": self.religion,
            "procedencia": self.procedencia,
            "telefono": self.telefono,
            "email": self.email,
            "direccion": self.direccion,
            "seguro": self.seguro,
            "fecha_registro": str(self.fecha_registro)
        }
