from flask import jsonify, request
from extensions.database import db
from models.cita_model import Cita
from models.paciente_model import Paciente
from datetime import datetime

class CitaController:

    @staticmethod
    def listar():
        try:
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)
            fecha = request.args.get('fecha') # YYYY-MM-DD
            doctor_id = request.args.get('doctor_id')
            area = request.args.get('area')
            estado = request.args.get('estado')
            paciente_dni = request.args.get('paciente_dni')

            query = Cita.query

            if fecha:
                try:
                    fecha_obj = datetime.strptime(fecha, "%Y-%m-%d").date()
                    query = query.filter(db.func.date(Cita.fecha_registro) == fecha_obj)
                except ValueError:
                    pass # Ignore invalid date format

            if doctor_id:
                query = query.filter_by(doctor_id=doctor_id)
            
            if area:
                query = query.filter(Cita.area.ilike(f"%{area}%"))

            if estado:
                query = query.filter_by(estado=estado)

            if paciente_dni:
                query = query.join(Paciente).filter(Paciente.dni == paciente_dni)

            # Ordenar por fecha de registro descendente (más recientes primero)
            query = query.order_by(Cita.fecha_registro.desc())

            pagination = query.paginate(page=page, per_page=per_page, error_out=False)

            data = []
            for cita in pagination.items:
                cita_dict = cita.to_dict()
                # Incluir datos básicos del paciente
                if cita.paciente:
                    cita_dict['paciente'] = {
                        "id": cita.paciente.id,
                        "nombres": cita.paciente.nombres,
                        "apellido_paterno": cita.paciente.apellido_paterno,
                        "apellido_materno": cita.paciente.apellido_materno,
                        "dni": cita.paciente.dni
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
    def obtener(id):
        try:
            cita = Cita.query.get(id)
            if not cita:
                return jsonify({"error": "Cita no encontrada"}), 404
            
            cita_dict = cita.to_dict()
            if cita.paciente:
                cita_dict['paciente'] = {
                    "id": cita.paciente.id,
                    "nombres": cita.paciente.nombres,
                    "apellido_paterno": cita.paciente.apellido_paterno,
                    "apellido_materno": cita.paciente.apellido_materno,
                    "dni": cita.paciente.dni
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
