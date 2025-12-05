from flask import Blueprint, request, jsonify
from db import get_connection

doctor_bp = Blueprint('doctors', __name__, url_prefix='/doctors')

@doctor_bp.route('/', methods=['GET'])
def get_all_doctors():
    conn = get_connection()
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT d.*, s.name AS specialty_name
            FROM doctors d
            JOIN specialties s ON d.specialty_id = s.id
        """)
        doctors = cursor.fetchall()
    conn.close()
    return jsonify(doctors)

@doctor_bp.route('/', methods=['POST'])
def create_doctor():
    data = request.json
    conn = get_connection()
    with conn.cursor() as cursor:
        cursor.execute("""
            INSERT INTO doctors (full_name, license_number, phone, email, specialty_id)
            VALUES (%s, %s, %s, %s, %s)
        """, (data['full_name'], data['license_number'], data.get('phone'),
              data.get('email'), data['specialty_id']))
        conn.commit()
    conn.close()
    return jsonify({'message': 'Doctor registrado correctamente'})
