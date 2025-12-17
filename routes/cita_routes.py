from flask import Blueprint
from controllers.cita_controller import CitaController
from middleware.auth_middleware import token_required

cita_bp = Blueprint("cita_bp", __name__)

@cita_bp.post("/")
def crear_cita():
    return CitaController.crear()

@cita_bp.get("/")
@token_required
def listar_citas():
    return CitaController.listar()

@cita_bp.get("/<int:id>")
@token_required
def obtener_cita(id):
    return CitaController.obtener(id)

@cita_bp.put("/<int:id>")
@token_required
def actualizar_cita(id):
    return CitaController.actualizar(id)

@cita_bp.delete("/<int:id>")
@token_required
def eliminar_cita(id):
    return CitaController.eliminar(id)

@cita_bp.get("/<int:id>/historial")
@token_required
def obtener_historial_cita(id):
    """
    Obtener el historial de cambios de estado de una cita.
    
    Returns:
        Lista de cambios de estado ordenados por fecha descendente,
        incluyendo quién realizó cada cambio.
    """
    return CitaController.obtener_historial(id)

@cita_bp.get("/confirmadas")
def obtener_citas_confirmadas():
    """
    Obtener citas confirmadas para impresión.
    Ordenadas por fecha de registro (orden de llegada).
    
    Query params:
    - fecha: YYYY-MM-DD (requerido)
    - area_id: ID del área (requerido)
    """
    return CitaController.obtener_citas_confirmadas_para_impresion()

@cita_bp.get("/confirmadas/pdf")
def generar_pdf_citas_confirmadas():
    """
    Generar PDF de citas confirmadas para impresión.
    Retorna un archivo PDF para descargar.
    
    Query params:
    - fecha: YYYY-MM-DD (requerido)
    - area_id: ID del área (requerido)
    """
    return CitaController.generar_pdf_citas_confirmadas()
