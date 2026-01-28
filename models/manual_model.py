from extensions.database import db
from datetime import datetime

class Manual(db.Model):
    __tablename__ = "manuales"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    url_drive = db.Column(db.Text, nullable=False)
    rol_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=True) # Opcional: para mostrar manuales según el rol
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relación opcional con rol
    rol = db.relationship('Rol', backref=db.backref('manuales', lazy=True))

    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "descripcion": self.descripcion,
            "url_drive": self.url_drive,
            "rol_id": self.rol_id,
            "rol_nombre": self.rol.nombre if self.rol else "General",
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
