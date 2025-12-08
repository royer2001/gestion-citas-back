from flask import jsonify, request
from extensions.database import db
from models.cita_model import Cita
from models.paciente_model import Paciente
from models.horario_medico_model import HorarioMedico
from models.area_model import Area
from datetime import datetime

class CitaController:

    @staticmethod
    def listar():
        """
        Listar citas con filtros y paginación.
        
        Query params:
        - page: Página actual (default: 1)
        - per_page: Items por página (default: 10)
        - fecha: Filtrar por fecha de cita (YYYY-MM-DD)
        - fecha_registro: Filtrar por fecha de registro (YYYY-MM-DD)
        - doctor_id: Filtrar por ID del doctor
        - area: Filtrar por nombre de área (búsqueda parcial)
        - area_id: Filtrar por ID de área
        - estado: Filtrar por estado (pendiente, confirmada, atendida, cancelada, referido)
        - paciente_dni: Filtrar por DNI del paciente
        - turno: Filtrar por turno ('M' o 'T')
        """
        try:
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)
            fecha = request.args.get('fecha')  # Fecha de la cita YYYY-MM-DD
            fecha_registro = request.args.get('fecha_registro')  # Fecha de registro YYYY-MM-DD
            doctor_id = request.args.get('doctor_id')
            area = request.args.get('area')
            area_id = request.args.get('area_id')
            estado = request.args.get('estado')
            paciente_dni = request.args.get('paciente_dni')
            turno = request.args.get('turno')

            query = Cita.query

            # Filtro por fecha de la cita
            if fecha:
                try:
                    fecha_obj = datetime.strptime(fecha, "%Y-%m-%d").date()
                    query = query.filter(Cita.fecha == fecha_obj)
                except ValueError:
                    pass

            # Filtro por fecha de registro
            if fecha_registro:
                try:
                    fecha_obj = datetime.strptime(fecha_registro, "%Y-%m-%d").date()
                    query = query.filter(db.func.date(Cita.fecha_registro) == fecha_obj)
                except ValueError:
                    pass

            if doctor_id:
                query = query.filter_by(doctor_id=doctor_id)
            
            # Filtro por área (por ID o por nombre)
            if area_id:
                query = query.filter_by(area_id=area_id)
            elif area:
                # Buscar por nombre de área (case-insensitive, parcial)
                query = query.outerjoin(Area, Cita.area_id == Area.id).filter(
                    db.or_(
                        Cita.area.ilike(f"%{area}%"),
                        Area.nombre.ilike(f"%{area}%")
                    )
                )

            if estado:
                query = query.filter_by(estado=estado)

            if paciente_dni:
                query = query.join(Paciente).filter(Paciente.dni.ilike(f"%{paciente_dni}%"))

            # Filtro por turno (si tiene horario asociado)
            if turno:
                query = query.join(HorarioMedico, Cita.horario_id == HorarioMedico.id).filter(
                    HorarioMedico.turno == turno
                )

            # Ordenar por fecha de cita descendente, luego por fecha_registro
            query = query.order_by(Cita.fecha.desc().nullslast(), Cita.fecha_registro.desc())

            pagination = query.paginate(page=page, per_page=per_page, error_out=False)

            data = []
            for cita in pagination.items:
                cita_dict = cita.to_dict()
                
                # Incluir datos del paciente
                if cita.paciente:
                    cita_dict['paciente'] = {
                        "id": cita.paciente.id,
                        "nombres": cita.paciente.nombres,
                        "apellido_paterno": cita.paciente.apellido_paterno,
                        "apellido_materno": cita.paciente.apellido_materno,
                        "dni": cita.paciente.dni,
                        "telefono": cita.paciente.telefono,
                        "email": cita.paciente.email
                    }
                
                # Incluir información del horario si existe
                if cita.horario:
                    cita_dict['horario'] = {
                        "id": cita.horario.id,
                        "turno": cita.horario.turno,
                        "turno_nombre": cita.horario.turno_nombre,
                        "hora_inicio": str(cita.horario.hora_inicio),
                        "hora_fin": str(cita.horario.hora_fin)
                    }
                
                data.append(cita_dict)

            return jsonify({
                "total": pagination.total,
                "pages": pagination.pages,
                "current_page": pagination.page,
                "per_page": pagination.per_page,
                "data": data
            }), 200

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @staticmethod
    def crear():
        """
        Crear una nueva cita médica.
        
        Payload esperado:
        {
            "paciente_id": int (requerido),
            "horario_id": int (requerido),
            "fecha": "YYYY-MM-DD" (requerido),
            "sintomas": string (requerido),
            "area_id": int (opcional, se obtiene del horario si no se envía),
            "dni_acompanante": string (opcional),
            "nombre_acompanante": string (opcional),
            "telefono_acompanante": string (opcional)
        }
        """
        try:
            data = request.get_json()
            
            # Validar campos requeridos
            required_fields = ["paciente_id", "horario_id", "fecha", "sintomas"]
            for field in required_fields:
                if field not in data or not data[field]:
                    return jsonify({"error": f"El campo '{field}' es obligatorio"}), 400
            
            # Validar que el paciente exista
            paciente = Paciente.query.get(data["paciente_id"])
            if not paciente:
                return jsonify({"error": "Paciente no encontrado"}), 404
            
            # Obtener el horario para validar y extraer información
            horario = HorarioMedico.query.get(data["horario_id"])
            if not horario:
                return jsonify({"error": "Horario no encontrado"}), 404
            
            # Parsear la fecha
            try:
                fecha_cita = datetime.strptime(data["fecha"], "%Y-%m-%d").date()
            except ValueError:
                return jsonify({"error": "Formato de fecha inválido. Use YYYY-MM-DD"}), 400
            
            # Validar que la fecha coincida con el horario
            if horario.fecha != fecha_cita:
                return jsonify({"error": "La fecha no coincide con el horario seleccionado"}), 400
            
            # Contar citas existentes para este horario en esta fecha
            citas_existentes = Cita.query.filter(
                Cita.horario_id == horario.id,
                Cita.fecha == fecha_cita,
                Cita.estado != 'cancelada'
            ).count()
            
            # Validar cupos disponibles
            if citas_existentes >= horario.cupos:
                return jsonify({
                    "error": "No hay cupos disponibles para este horario",
                    "cupos_totales": horario.cupos,
                    "cupos_ocupados": citas_existentes
                }), 400
            
            # Determinar area_id (del payload o del horario)
            area_id = data.get("area_id") or horario.area_id
            
            # Obtener nombre del área
            area = Area.query.get(area_id)
            area_nombre = area.nombre if area else "Sin área"
            
            # Crear la cita
            nueva_cita = Cita(
                paciente_id=data["paciente_id"],
                horario_id=horario.id,
                doctor_id=horario.medico_id,
                area_id=area_id,
                area=area_nombre,
                fecha=fecha_cita,
                sintomas=data["sintomas"],
                dni_acompanante=data.get("dni_acompanante"),
                nombre_acompanante=data.get("nombre_acompanante"),
                telefono_acompanante=data.get("telefono_acompanante"),
                datos_adicionales=data.get("datos_adicionales"),
                estado="pendiente"
            )
            
            db.session.add(nueva_cita)
            db.session.commit()
            
            # Calcular cupos restantes para la respuesta
            cupos_restantes = horario.cupos - (citas_existentes + 1)
            
            return jsonify({
                "message": "Cita creada exitosamente",
                "data": nueva_cita.to_dict(),
                "cupos_restantes": cupos_restantes
            }), 201
            
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500

    @staticmethod
    def obtener(id):
        """
        Obtener detalle completo de una cita por ID.
        Incluye información del paciente, horario y doctor.
        """
        try:
            cita = Cita.query.get(id)
            if not cita:
                return jsonify({"error": "Cita no encontrada"}), 404
            
            cita_dict = cita.to_dict()
            
            # Incluir datos completos del paciente
            if cita.paciente:
                cita_dict['paciente'] = {
                    "id": cita.paciente.id,
                    "nombres": cita.paciente.nombres,
                    "apellido_paterno": cita.paciente.apellido_paterno,
                    "apellido_materno": cita.paciente.apellido_materno,
                    "dni": cita.paciente.dni,
                    "telefono": cita.paciente.telefono,
                    "email": cita.paciente.email,
                    "fecha_nacimiento": str(cita.paciente.fecha_nacimiento) if cita.paciente.fecha_nacimiento else None,
                    "sexo": cita.paciente.sexo,
                    "direccion": cita.paciente.direccion,
                    "seguro": cita.paciente.seguro
                }
            
            # Incluir información del horario si existe
            if cita.horario:
                cita_dict['horario'] = {
                    "id": cita.horario.id,
                    "turno": cita.horario.turno,
                    "turno_nombre": cita.horario.turno_nombre,
                    "hora_inicio": str(cita.horario.hora_inicio),
                    "hora_fin": str(cita.horario.hora_fin),
                    "cupos": cita.horario.cupos
                }
            
            return jsonify(cita_dict), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @staticmethod
    def actualizar(id):
        try:
            data = request.get_json()
            cita = Cita.query.get(id)
            if not cita:
                return jsonify({"error": "Cita no encontrada"}), 404

            if "doctor_id" in data:
                cita.doctor_id = data["doctor_id"]
            if "area" in data:
                cita.area = data["area"]
            if "sintomas" in data:
                cita.sintomas = data["sintomas"]
            if "estado" in data:
                cita.estado = data["estado"]
            if "dni_acompanante" in data:
                cita.dni_acompanante = data["dni_acompanante"]
            if "nombre_acompanante" in data:
                cita.nombre_acompanante = data["nombre_acompanante"]
            if "telefono_acompanante" in data:
                cita.telefono_acompanante = data["telefono_acompanante"]
            if "datos_adicionales" in data:
                # Merge or replace? Usually replace or merge. Let's assume replace for now or update keys.
                # If it's a dict, we might want to update.
                if cita.datos_adicionales and isinstance(data["datos_adicionales"], dict):
                    cita.datos_adicionales.update(data["datos_adicionales"])
                else:
                    cita.datos_adicionales = data["datos_adicionales"]

            db.session.commit()
            return jsonify(cita.to_dict()), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500

    @staticmethod
    def eliminar(id):
        try:
            cita = Cita.query.get(id)
            if not cita:
                return jsonify({"error": "Cita no encontrada"}), 404
            
            db.session.delete(cita)
            db.session.commit()
            return jsonify({"message": "Cita eliminada correctamente"}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500
