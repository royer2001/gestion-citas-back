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
                paciente.ocupacion = data.get("ocupacion")
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
                    ocupacion=data.get("ocupacion"),
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

    @staticmethod
    def obtener_por_id(paciente_id):
        """
        Obtener un paciente por su ID.
        """
        try:
            paciente = Paciente.query.get(paciente_id)
            
            if not paciente:
                return jsonify({"error": "Paciente no encontrado"}), 404
            
            return jsonify(paciente.to_dict()), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @staticmethod
    def actualizar(paciente_id, data):
        """
        Actualizar datos de un paciente existente.
        
        Body JSON:
        - nombres: Nombres del paciente
        - apellido_paterno: Apellido paterno
        - apellido_materno: Apellido materno
        - fecha_nacimiento: Fecha de nacimiento (YYYY-MM-DD)
        - sexo: M o F
        - estado_civil: S, C, V, D
        - grado_instruccion: Nivel educativo
        - religion, procedencia, ocupacion: Datos adicionales
        - telefono, email, direccion: Contacto
        - seguro, numero_seguro: Información de seguro
        """
        try:
            paciente = Paciente.query.get(paciente_id)
            
            if not paciente:
                return jsonify({"error": "Paciente no encontrado"}), 404

            # Actualizar campos proporcionados
            if "nombres" in data:
                paciente.nombres = data["nombres"]
            if "apellido_paterno" in data:
                paciente.apellido_paterno = data["apellido_paterno"]
            if "apellido_materno" in data:
                paciente.apellido_materno = data["apellido_materno"]
            if "fecha_nacimiento" in data:
                paciente.fecha_nacimiento = datetime.strptime(data["fecha_nacimiento"], "%Y-%m-%d")
            if "sexo" in data:
                paciente.sexo = data["sexo"]
            if "estado_civil" in data:
                paciente.estado_civil = data["estado_civil"]
            if "grado_instruccion" in data:
                paciente.grado_instruccion = data["grado_instruccion"]
            if "religion" in data:
                paciente.religion = data["religion"]
            if "procedencia" in data:
                paciente.procedencia = data["procedencia"]
            if "ocupacion" in data:
                paciente.ocupacion = data["ocupacion"]
            if "telefono" in data:
                paciente.telefono = data["telefono"]
            if "email" in data:
                paciente.email = data["email"]
            if "direccion" in data:
                paciente.direccion = data["direccion"]
            if "seguro" in data:
                paciente.seguro = data["seguro"]
            if "numero_seguro" in data:
                paciente.numero_seguro = data["numero_seguro"]

            db.session.commit()

            return jsonify({
                "message": "Paciente actualizado correctamente",
                "data": paciente.to_dict()
            }), 200

        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500

    @staticmethod
    def obtener_historial_citas(paciente_id):
        """
        Obtener el historial de citas de un paciente.
        
        Query params:
        - page: Página actual (default: 1)
        - per_page: Items por página (default: 10)
        - estado: Filtrar por estado (pendiente, confirmada, atendida, cancelada, referido)
        
        Retorna lista de citas ordenadas por fecha descendente.
        """
        try:
            from flask import request
            
            # Verificar que el paciente existe
            paciente = Paciente.query.get(paciente_id)
            if not paciente:
                return jsonify({"error": "Paciente no encontrado"}), 404

            # Parámetros de paginación
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)
            estado = request.args.get('estado', '', type=str)

            # Construir query
            query = Cita.query.filter_by(paciente_id=paciente_id)

            # Filtro por estado
            if estado:
                query = query.filter(Cita.estado == estado)

            # Ordenar por fecha de cita descendente (más recientes primero)
            query = query.order_by(Cita.fecha.desc(), Cita.fecha_registro.desc())

            pagination = query.paginate(page=page, per_page=per_page, error_out=False)

            # Construir respuesta con datos enriquecidos
            citas_data = []
            for cita in pagination.items:
                cita_dict = cita.to_dict()
                
                # Agregar información del horario si existe
                if cita.horario:
                    cita_dict["horario"] = {
                        "id": cita.horario.id,
                        "turno": cita.horario.turno,
                        "turno_nombre": cita.horario.turno_nombre,
                        "hora_inicio": str(cita.horario.hora_inicio),
                        "hora_fin": str(cita.horario.hora_fin)
                    }
                
                citas_data.append(cita_dict)

            return jsonify({
                "paciente": {
                    "id": paciente.id,
                    "dni": paciente.dni,
                    "nombre_completo": f"{paciente.apellido_paterno} {paciente.apellido_materno}, {paciente.nombres}"
                },
                "total": pagination.total,
                "pages": pagination.pages,
                "current_page": pagination.page,
                "per_page": pagination.per_page,
                "data": citas_data
            }), 200

        except Exception as e:
            return jsonify({"error": str(e)}), 500

