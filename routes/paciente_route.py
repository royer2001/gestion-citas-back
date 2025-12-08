from flask import Blueprint, request
from controllers.paciente_controller import PacienteController

paciente_bp = Blueprint("paciente_bp", __name__)

@paciente_bp.post("/")
def registrar_paciente():
    data = request.get_json()
    return PacienteController.registrar(data)

@paciente_bp.get("/")
def listar_pacientes():
    return PacienteController.listar()

@paciente_bp.get("/buscar/<dni>")
def buscar_paciente(dni):
    return PacienteController.buscar_por_dni(dni)

@paciente_bp.get("/<int:paciente_id>")
def obtener_paciente(paciente_id):
    """Obtiene un paciente específico por su ID."""
    return PacienteController.obtener_por_id(paciente_id)

@paciente_bp.put("/<int:paciente_id>")
def actualizar_paciente(paciente_id):
    """Actualiza los datos de un paciente existente."""
    data = request.get_json()
    return PacienteController.actualizar(paciente_id, data)

@paciente_bp.get("/<int:paciente_id>/historial")
def obtener_historial_paciente(paciente_id):
    """Obtiene el historial de citas de un paciente."""
    return PacienteController.obtener_historial_citas(paciente_id)
