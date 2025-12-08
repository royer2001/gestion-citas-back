from flask import Blueprint, jsonify
from controllers.dashboard_controller import (
    get_dashboard_stats,
    get_upcoming_appointments,
    get_appointments_by_specialty_today
)

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/stats', methods=['GET'])
def stats():
    try:
        data = get_dashboard_stats()
        return jsonify(data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/upcoming-appointments', methods=['GET'])
def upcoming_appointments():
    try:
        data = get_upcoming_appointments()
        return jsonify(data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/appointments-by-specialty', methods=['GET'])
def appointments_by_specialty():
    try:
        data = get_appointments_by_specialty_today()
        return jsonify(data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
