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
