from flask import Blueprint, jsonify, request
from controllers.dashboard_controller import (
    get_dashboard_stats,
    get_upcoming_appointments,
    get_appointments_by_specialty_today
)
from middleware.auth_middleware import token_required

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/stats', methods=['GET'])
@token_required
def stats():
    try:
        data = get_dashboard_stats()
        return jsonify(data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/upcoming-appointments', methods=['GET'])
@token_required
def upcoming_appointments():
    try:
        user_rol_id = request.user.get('rol_id') if hasattr(request, 'user') else None
        user_id = request.user.get('id') if hasattr(request, 'user') else None
        
        data = get_upcoming_appointments(user_rol_id, user_id)
        return jsonify(data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/appointments-by-specialty', methods=['GET'])
@token_required
def appointments_by_specialty():
    try:
        data = get_appointments_by_specialty_today()
        return jsonify(data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
