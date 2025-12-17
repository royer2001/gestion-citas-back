from extensions.database import db
from datetime import datetime

class HistorialEstadoCita(db.Model):
    """
    Modelo para registrar el historial de cambios de estado de las citas.
    Cada vez que una cita cambia de estado, se registra aquí con:
    - El estado anterior y el nuevo estado
    - El usuario que realizó el cambio
    - La fecha y hora del cambio
    - Opcionalmente, un comentario o motivo
    """
    __tablename__ = "historial_estado_citas"

    id = db.Column(db.Integer, primary_key=True)
    cita_id = db.Column(db.Integer, db.ForeignKey('citas.id'), nullable=False)
    estado_anterior = db.Column(db.String(20), nullable=True)  # Null para el estado inicial
    estado_nuevo = db.Column(db.String(20), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True)  # Quien hizo el cambio
    fecha_cambio = db.Column(db.DateTime, default=datetime.utcnow)
    comentario = db.Column(db.Text, nullable=True)  # Motivo opcional del cambio
    ip_address = db.Column(db.String(45), nullable=True)  # IP del cliente (opcional)

    # Relaciones
    cita = db.relationship('Cita', backref=db.backref('historial_estados', lazy='dynamic', order_by='HistorialEstadoCita.fecha_cambio.desc()'))
    usuario = db.relationship('Usuario', backref=db.backref('cambios_estado_citas', lazy=True))

    def to_dict(self):
        return {
            "id": self.id,
            "cita_id": self.cita_id,
            "estado_anterior": self.estado_anterior,
            "estado_nuevo": self.estado_nuevo,
            "usuario_id": self.usuario_id,
            "usuario_nombre": self.usuario.nombres_completos if self.usuario else "Sistema",
            "fecha_cambio": self.fecha_cambio.isoformat() if self.fecha_cambio else None,
            "comentario": self.comentario,
            "ip_address": self.ip_address
        }

    @staticmethod
    def registrar_cambio(cita_id, estado_anterior, estado_nuevo, usuario_id=None, comentario=None, ip_address=None):
        """
        Método estático para registrar un cambio de estado de manera sencilla.
        
        Args:
            cita_id: ID de la cita
            estado_anterior: Estado previo de la cita (None para creación)
            estado_nuevo: Nuevo estado de la cita
            usuario_id: ID del usuario que realiza el cambio
            comentario: Comentario o motivo opcional
            ip_address: IP del cliente (opcional)
        
        Returns:
            El registro de historial creado
        """
        historial = HistorialEstadoCita(
            cita_id=cita_id,
            estado_anterior=estado_anterior,
            estado_nuevo=estado_nuevo,
            usuario_id=usuario_id,
            comentario=comentario,
            ip_address=ip_address
        )
        db.session.add(historial)
        return historial
