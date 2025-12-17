from flask import Blueprint
from controllers.usuario_controller import UsuarioController
from middleware.auth_middleware import token_required

medico_bp = Blueprint("medico_bp", __name__)

@medico_bp.get("/")
@token_required
def get_medicos():
    """
    Obtiene lista de profesionales.
    Soporta filtro por area_id a través de query params.
    """
    return UsuarioController.get_medicos()
