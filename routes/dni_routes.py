from flask import Blueprint
from controllers.dni_controller import DniController

dni_bp = Blueprint('dni_bp', __name__)

dni_bp.route('/', methods=['POST'])(DniController.index)
