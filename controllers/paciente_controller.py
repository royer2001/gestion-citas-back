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
        try:
            # Validación básica de campos requeridos para Paciente
            required = [
                "dni", "nombres", "apellido_paterno", "apellido_materno",
                "fecha_nacimiento", "sexo", "estado_civil",
                "direccion", "sintomas"
            ]

            for field in required:
                if field not in data or not data[field]:
                    return jsonify({"error": f"El campo '{field}' es obligatorio"}), 400

            # Verificar si el paciente ya existe
            paciente = Paciente.query.filter_by(dni=data["dni"]).first()

            # Definir campos conocidos
            known_fields = {
                "dni", "nombres", "apellido_paterno", "apellido_materno",
                "fecha_nacimiento", "sexo", "estado_civil", "grado_instruccion",
                "religion", "procedencia", "telefono", "email", "direccion",
                "dni_acompanante", "nombre_acompanante", "telefono_acompanante",
                "sintomas", "seguro"
            }

            # Campos específicos de la cita que no queremos en datos_adicionales del paciente
            cita_fields = {"doctor_asignado_id", "area_atencion", "doctor_asignado_nombre"}
            
            # Capturar datos adicionales
            datos_adicionales = {k: v for k, v in data.items() if k not in known_fields and k not in cita_fields}

            # Mapeo de campos del frontend a campos del modelo
            dni_acompanante = data.get("dni_acompanante") or data.get("dni_contacto_emergencia")
            nombre_acompanante = data.get("nombre_acompanante") or data.get("contacto_emergencia")
            telefono_acompanante = data.get("telefono_acompanante") or data.get("telefono_contacto_emergencia")

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
                # paciente.dni_acompanante = dni_acompanante # Removed
                # paciente.nombre_acompanante = nombre_acompanante # Removed
                # paciente.telefono_acompanante = telefono_acompanante # Removed
                # paciente.sintomas = data["sintomas"] # Removed from Paciente
                paciente.seguro = data.get("seguro")
                # paciente.datos_adicionales = datos_adicionales if datos_adicionales else None # Removed
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
                    # dni_acompanante=dni_acompanante, # Removed
                    # nombre_acompanante=nombre_acompanante, # Removed
                    # telefono_acompanante=telefono_acompanante, # Removed
                    # sintomas=data["sintomas"], # Removed from Paciente
                    seguro=data.get("seguro"),
                    # datos_adicionales=datos_adicionales if datos_adicionales else None # Removed
                )
                db.session.add(paciente)
            
            # Guardar cambios del paciente (insert o update)
            db.session.flush() # Para obtener el ID del paciente si es nuevo

            # Crear la Cita
            doctor_id = data.get("doctor_asignado_id")
            if doctor_id:
                # Validar horario y cupos
                from models.horario_medico_model import HorarioMedico
                
                # Asumimos que la cita es para HOY (Local Time)
                now_local = datetime.now()
                dia_semana = now_local.weekday() # 0=Monday
                
                horario = HorarioMedico.query.filter_by(
                    medico_id=doctor_id,
                    dia_semana=dia_semana
                ).first()

                if not horario:
                    return jsonify({"error": "El médico no tiene turno programado para hoy"}), 400
                
                # Validar hora (opcional, si se quiere restringir registro fuera de horario)
                current_time = now_local.time()
                if current_time < horario.hora_inicio or current_time > horario.hora_fin:
                     return jsonify({"error": f"El médico atiende de {horario.hora_inicio} a {horario.hora_fin}"}), 400

                # Validar cupos
                # Calcular rango del día en UTC para comparar con fecha_registro (que está en UTC)
                # Estimamos offset: Local - UTC
                utcnow = datetime.utcnow()
                offset = now_local - utcnow
                
                start_day_local = now_local.replace(hour=0, minute=0, second=0, microsecond=0)
                end_day_local = now_local.replace(hour=23, minute=59, second=59, microsecond=999999)
                
                # Aproximación: si offset es negativo (ej. Peru -5), al restar offset (que es negativo) sumamos 5 horas?
                # No, offset = Local - UTC.  => Local = UTC + offset => UTC = Local - offset.
                start_day_utc = start_day_local - offset
                end_day_utc = end_day_local - offset
                
                citas_hoy = Cita.query.filter(
                    Cita.doctor_id == doctor_id,
                    Cita.fecha_registro >= start_day_utc,
                    Cita.fecha_registro <= end_day_utc
                ).count()

                if citas_hoy >= horario.cupos:
                    return jsonify({"error": f"No hay cupos disponibles para este médico hoy (Máx: {horario.cupos})"}), 400

            cita = Cita(
                paciente_id=paciente.id,
                doctor_id=doctor_id,
                area=data.get("area_atencion", "Pendiente"),
                sintomas=data["sintomas"],
                dni_acompanante=dni_acompanante,
                nombre_acompanante=nombre_acompanante,
                telefono_acompanante=telefono_acompanante,
                datos_adicionales=datos_adicionales if datos_adicionales else None
            )
            db.session.add(cita)

            db.session.commit()

            return jsonify({
                "message": "Paciente registrado y cita asignada correctamente",
                "data": {
                    "paciente": paciente.to_dict(),
                    "cita": cita.to_dict()
                }
            }), 201

        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500
