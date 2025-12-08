from flask import jsonify
from extensions.database import db
from models.paciente_model import Paciente
from models.cita_model import Cita
from datetime import datetime

class PacienteController:

    @staticmethod
    def buscar_por_dni(dni):
        try:
            # 1. Buscar en BD local
            paciente = Paciente.query.filter_by(dni=dni).first()
            if paciente:
                return jsonify(paciente.to_dict()), 200
            
            # 2. Si no existe, buscar en API externa
            from services.api_dni_services import ApiPeruDevService
            api_response = ApiPeruDevService.get_data_by_dni(dni)
            
            if api_response.get("success"):
                data = api_response.get("data", {})
                return jsonify({
                    "dni": dni,
                    "nombres": data.get("nombres"),
                    "apellido_paterno": data.get("apellido_paterno"),
                    "apellido_materno": data.get("apellido_materno"),
                    "origen": "reniec" # Indicador para el frontend
                }), 200

            return jsonify({"error": "Paciente no encontrado"}), 404
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @staticmethod
    def listar():
        try:
            from flask import request
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)
            search = request.args.get('search', '', type=str)

            query = Paciente.query

            if search:
                search_term = f"%{search}%"
                query = query.filter(
                    (Paciente.dni.ilike(search_term)) |
                    (Paciente.nombres.ilike(search_term)) |
                    (Paciente.apellido_paterno.ilike(search_term)) |
                    (Paciente.apellido_materno.ilike(search_term))
                )

            # Ordenar por fecha de registro descendente (más recientes primero)
            query = query.order_by(Paciente.fecha_registro.desc())

            pagination = query.paginate(page=page, per_page=per_page, error_out=False)

            return jsonify({
                "total": pagination.total,
                "pages": pagination.pages,
                "current_page": pagination.page,
                "per_page": pagination.per_page,
                "data": [p.to_dict() for p in pagination.items]
            }), 200

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @staticmethod
    def registrar(data):
        """
        Registrar o actualizar un paciente.
        
        Si el paciente ya existe (por DNI), se actualizan sus datos.
        Si no existe, se crea uno nuevo.
        
        La creación de citas se realiza por separado mediante POST /api/citas
        """
        try:
            # Validación básica de campos requeridos para Paciente
            required = [
                "dni", "nombres", "apellido_paterno", "apellido_materno",
                "fecha_nacimiento", "sexo", "estado_civil", "direccion"
            ]

            for field in required:
                if field not in data or not data[field]:
                    return jsonify({"error": f"El campo '{field}' es obligatorio"}), 400

            # Verificar si el paciente ya existe
            paciente = Paciente.query.filter_by(dni=data["dni"]).first()
            is_new = paciente is None

            if paciente:
                # Actualizar datos del paciente existente
                paciente.nombres = data["nombres"]
                paciente.apellido_paterno = data["apellido_paterno"]
                paciente.apellido_materno = data["apellido_materno"]
                paciente.fecha_nacimiento = datetime.strptime(data["fecha_nacimiento"], "%Y-%m-%d")
                paciente.sexo = data["sexo"]
                paciente.estado_civil = data["estado_civil"]
                paciente.grado_instruccion = data.get("grado_instruccion")
                paciente.religion = data.get("religion")
                paciente.procedencia = data.get("procedencia")
                paciente.telefono = data.get("telefono")
                paciente.email = data.get("email")
                paciente.direccion = data["direccion"]
                paciente.seguro = data.get("seguro")
                paciente.numero_seguro = data.get("numero_seguro")
            else:
                # Crear nuevo paciente
                paciente = Paciente(
                    dni=data["dni"],
                    nombres=data["nombres"],
                    apellido_paterno=data["apellido_paterno"],
                    apellido_materno=data["apellido_materno"],
                    fecha_nacimiento=datetime.strptime(data["fecha_nacimiento"], "%Y-%m-%d"),
                    sexo=data["sexo"],
                    estado_civil=data["estado_civil"],
                    grado_instruccion=data.get("grado_instruccion"),
                    religion=data.get("religion"),
                    procedencia=data.get("procedencia"),
                    telefono=data.get("telefono"),
                    email=data.get("email"),
                    direccion=data["direccion"],
                    seguro=data.get("seguro"),
                    numero_seguro=data.get("numero_seguro"),
                )
                db.session.add(paciente)
            
            db.session.commit()

            return jsonify({
                "message": "Paciente actualizado correctamente" if not is_new else "Paciente registrado correctamente",
                "id": paciente.id,
                "is_new": is_new,
                "data": paciente.to_dict()
            }), 201 if is_new else 200

        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500

