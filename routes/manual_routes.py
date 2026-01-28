from flask import Blueprint
from controllers.manual_controller import (
    get_manuales,
    create_manual,
    update_manual,
    delete_manual,
    get_manuales_por_rol
)
from middleware.auth_middleware import token_required

manual_bp = Blueprint('manual_bp', __name__)

# Rutas públicas o protegidas según necesidad. 
# Asumiremos que visualizar es para autenticados, crear/editar para admin (se puede refinar en el controller o middleware)

@manual_bp.route('/', methods=['GET'])
@token_required
def index():
    return get_manuales()

@manual_bp.route('/rol/<int:rol_id>', methods=['GET'])
@token_required
def by_rol(rol_id):
    return get_manuales_por_rol(rol_id)

@manual_bp.route('/', methods=['POST'])
@token_required
def store():
    return create_manual()

@manual_bp.route('/<int:id>', methods=['PUT'])
@token_required
def update(id):
    return update_manual(id)

@manual_bp.route('/<int:id>', methods=['DELETE'])
@token_required
def destroy(id):
    return delete_manual(id)
