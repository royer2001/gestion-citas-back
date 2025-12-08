from flask import Blueprint
from controllers.cita_controller import CitaController

cita_bp = Blueprint("cita_bp", __name__)

@cita_bp.post("/")
def crear_cita():
    return CitaController.crear()

@cita_bp.get("/")
def listar_citas():
    return CitaController.listar()

@cita_bp.get("/<int:id>")
def obtener_cita(id):
    return CitaController.obtener(id)

@cita_bp.put("/<int:id>")
def actualizar_cita(id):
    return CitaController.actualizar(id)

@cita_bp.delete("/<int:id>")
def eliminar_cita(id):
    return CitaController.eliminar(id)
