from extensions.database import db
from datetime import datetime

class Usuario(db.Model):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    dni = db.Column(db.String(8), unique=True, nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=True)  # opcional ahora
    password = db.Column(db.Text, nullable=False)
    nombres_completos = db.Column(db.String(150), nullable=True)
    
    rol_id = db.Column(db.Integer, nullable=False)  
    # valores: 1 = administrador, 2 = medico, 3 = asistente

    activo = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "dni": self.dni,
            "username": self.username,
            "nombres_completos": self.nombres_completos,
            "rol_id": self.rol_id,
            "activo": self.activo,
            # "fecha_creacion": str(self.fecha_creacion)
        }
