from flask import jsonify, request
from services.api_dni_services import ApiPeruDevService

class DniController:
    @staticmethod
    def index():
        data = request.get_json()
        dni = data.get("dni")

        if not dni:
            return jsonify({"error": "dni es requerido"}), 400

        if not isinstance(dni, str) or len(dni) != 8 or not dni.isdigit():
            return jsonify({"error": "dni debe ser una cadena de 8 dígitos"}), 400

        result = ApiPeruDevService.get_data_by_dni(dni)

        # Si la API respondió mal
        if not result.get("success"):
            return jsonify({"error": "No se pudo obtener datos del DNI", "detalle": result}), 500

        # Extraer los campos solicitados
        data_person = result.get("data", {})

        response_data = {
            "nombres": data_person.get("nombres"),
            "apellido_paterno": data_person.get("apellido_paterno"),
            "apellido_materno": data_person.get("apellido_materno")
        }

        return jsonify(response_data)
