from flask import request, jsonify
from extensions.database import db
from models.horario_medico_model import HorarioMedico
from models.usuario_model import Usuario
from models.area_model import Area
from datetime import datetime, date
from calendar import monthrange

class HorarioController:

    @staticmethod
    def create_horarios_mensuales():
        """
        Crea horarios para todo un mes.
        
        Payload esperado:
        {
            "medico_id": 1,
            "area_id": 1,
            "mes": "2025-01",  # YYYY-MM
            "dias_seleccionados": [0, 1, 2, 3, 4],  # 0=Lun, 1=Mar, ..., 6=Dom
            "turnos": {
                "manana": {
                    "activo": true,
                    "cupos": 5
                },
                "tarde": {
                    "activo": true,
                    "cupos": 7
                }
            }
        }
        """
        try:
            data = request.json
            
            medico_id = data.get("medico_id")
            area_id = data.get("area_id")
            mes_str = data.get("mes")  # Formato "YYYY-MM"
            dias_seleccionados = data.get("dias_seleccionados", [])
            turnos = data.get("turnos", {})
            
            # Validaciones
            if not all([medico_id, area_id, mes_str, dias_seleccionados]):
                return jsonify({"error": "Faltan datos obligatorios: medico_id, area_id, mes, dias_seleccionados"}), 400
            
            # Validar que al menos un turno esté activo
            turno_manana = turnos.get("manana", {})
            turno_tarde = turnos.get("tarde", {})
            
            if not turno_manana.get("activo") and not turno_tarde.get("activo"):
                return jsonify({"error": "Debe activar al menos un turno (mañana o tarde)"}), 400
            
            # Parsear mes
            try:
                year, month = map(int, mes_str.split("-"))
            except ValueError:
                return jsonify({"error": "Formato de mes inválido. Use YYYY-MM"}), 400
            
            # Obtener días del mes
            _, dias_en_mes = monthrange(year, month)
            
            horarios_creados = []
            horarios_actualizados = []
            
            for dia in range(1, dias_en_mes + 1):
                fecha_actual = date(year, month, dia)
                # Calcular día de la semana (0=Lun, ..., 6=Dom)
                dia_semana = fecha_actual.weekday()
                
                if dia_semana in dias_seleccionados:
                    # Procesar turno mañana
                    if turno_manana.get("activo"):
                        resultado = HorarioController._crear_o_actualizar_horario(
                            medico_id=medico_id,
                            area_id=area_id,
                            fecha=fecha_actual,
                            dia_semana=dia_semana,
                            turno='M',
                            cupos=turno_manana.get("cupos", 5)
                        )
                        if resultado["is_new"]:
                            horarios_creados.append(resultado["horario"])
                        else:
                            horarios_actualizados.append(resultado["horario"])
                    
                    # Procesar turno tarde
                    if turno_tarde.get("activo"):
                        resultado = HorarioController._crear_o_actualizar_horario(
                            medico_id=medico_id,
                            area_id=area_id,
                            fecha=fecha_actual,
                            dia_semana=dia_semana,
                            turno='T',
                            cupos=turno_tarde.get("cupos", 7)
                        )
                        if resultado["is_new"]:
                            horarios_creados.append(resultado["horario"])
                        else:
                            horarios_actualizados.append(resultado["horario"])
            
            db.session.commit()
            
            return jsonify({
                "message": f"Horarios procesados correctamente",
                "creados": len(horarios_creados),
                "actualizados": len(horarios_actualizados),
                "horarios": [h.to_dict() for h in horarios_creados + horarios_actualizados]
            }), 201
            
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500

    @staticmethod
    def _crear_o_actualizar_horario(medico_id, area_id, fecha, dia_semana, turno, cupos):
        """Crea o actualiza un horario individual"""
        horario_existente = HorarioMedico.query.filter_by(
            medico_id=medico_id,
            fecha=fecha,
            turno=turno
        ).first()
        
        if horario_existente:
            horario_existente.area_id = area_id
            horario_existente.cupos = cupos
            return {"horario": horario_existente, "is_new": False}
        else:
            nuevo_horario = HorarioMedico(
                medico_id=medico_id,
                area_id=area_id,
                fecha=fecha,
                dia_semana=dia_semana,
                turno=turno,
                cupos=cupos
            )
            db.session.add(nuevo_horario)
            return {"horario": nuevo_horario, "is_new": True}

    @staticmethod
    def create_or_update_horario():
        """
        Crea o actualiza horarios individuales (compatibilidad con estructura anterior).
        También acepta el nuevo formato con turnos.
        """
        try:
            data = request.json
            
            # Si es el nuevo formato mensual, redirigir
            if "turnos" in data:
                return HorarioController.create_horarios_mensuales()
            
            if isinstance(data, list):
                # Procesamiento masivo (formato legacy)
                results = []
                for item in data:
                    res = HorarioController._process_single_horario(item)
                    results.append(res)
                
                db.session.commit()
                return jsonify({
                    "message": f"{len(results)} horarios procesados correctamente", 
                    "horarios": [r.to_dict() for r in results]
                }), 201
            else:
                # Procesamiento individual
                res = HorarioController._process_single_horario(data)
                db.session.commit()
                return jsonify({
                    "message": "Horario procesado correctamente", 
                    "horario": res.to_dict()
                }), 201

        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500

    @staticmethod
    def _process_single_horario(data):
        """Procesa un horario individual con el nuevo formato"""
        medico_id = data.get("medico_id")
        area_id = data.get("area_id")
        fecha_str = data.get("fecha")  # Formato "YYYY-MM-DD"
        turno = data.get("turno", "M")  # 'M' o 'T'
        cupos = data.get("cupos", 5)
        
        # Soporte legacy: si no hay fecha pero hay dia_semana
        dia_semana = data.get("dia_semana")
        
        if fecha_str:
            try:
                fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
                dia_semana = fecha.weekday()
            except ValueError:
                raise Exception("Formato de fecha inválido. Use YYYY-MM-DD")
        else:
            raise Exception("Se requiere el campo 'fecha' en formato YYYY-MM-DD")

        if not all([medico_id, area_id, dia_semana is not None, cupos]):
            raise Exception("Faltan datos obligatorios")

        # Buscamos si ya existe horario para este medico en esta fecha y turno
        horario_existente = HorarioMedico.query.filter_by(
            medico_id=medico_id, 
            fecha=fecha,
            turno=turno
        ).first()

        if horario_existente:
            # Actualizar
            horario_existente.area_id = area_id
            horario_existente.cupos = cupos
            return horario_existente
        else:
            # Crear nuevo
            nuevo_horario = HorarioMedico(
                medico_id=medico_id,
                area_id=area_id,
                fecha=fecha,
                dia_semana=dia_semana,
                turno=turno,
                cupos=cupos
            )
            db.session.add(nuevo_horario)
            return nuevo_horario

    @staticmethod
    def get_horarios():
        """
        Obtiene horarios con filtros opcionales.
        Incluye cupos_disponibles calculado en base a citas activas.
        OPTIMIZADO: Una sola consulta con LEFT JOIN para calcular cupos.
        
        Query params:
        - medico_id: Filtrar por médico
        - area_id: Filtrar por área
        - mes: Filtrar por mes (formato YYYY-MM)
        - fecha: Filtrar por fecha específica (formato YYYY-MM-DD)
        - turno: Filtrar por turno ('M' o 'T')
        """
        try:
            from models.cita_model import Cita
            from sqlalchemy import func, case
            
            medico_id = request.args.get('medico_id')
            area_id = request.args.get('area_id')
            mes = request.args.get('mes')  # Formato YYYY-MM
            fecha = request.args.get('fecha')  # Formato YYYY-MM-DD
            turno = request.args.get('turno')  # 'M' o 'T'
            
            # Subconsulta para contar citas activas por horario_id
            # Cuenta solo citas no canceladas
            citas_count_subq = db.session.query(
                Cita.horario_id,
                func.count(Cita.id).label('citas_activas')
            ).filter(
                Cita.estado != 'cancelada'
            ).group_by(Cita.horario_id).subquery()
            
            # Query principal con LEFT JOIN a la subconsulta
            query = db.session.query(
                HorarioMedico,
                func.coalesce(citas_count_subq.c.citas_activas, 0).label('citas_activas')
            ).outerjoin(
                citas_count_subq,
                HorarioMedico.id == citas_count_subq.c.horario_id
            )
            
            # Aplicar filtros
            if medico_id:
                query = query.filter(HorarioMedico.medico_id == medico_id)
            
            if area_id:
                query = query.filter(HorarioMedico.area_id == area_id)
            
            if turno:
                query = query.filter(HorarioMedico.turno == turno)
            
            if fecha:
                try:
                    fecha_obj = datetime.strptime(fecha, "%Y-%m-%d").date()
                    query = query.filter(HorarioMedico.fecha == fecha_obj)
                except ValueError:
                    return jsonify({"error": "Formato de fecha inválido. Use YYYY-MM-DD"}), 400
            elif mes:
                try:
                    year, month = map(int, mes.split("-"))
                    fecha_inicio = date(year, month, 1)
                    _, dias_en_mes = monthrange(year, month)
                    fecha_fin = date(year, month, dias_en_mes)
                    query = query.filter(
                        HorarioMedico.fecha >= fecha_inicio,
                        HorarioMedico.fecha <= fecha_fin
                    )
                except ValueError:
                    return jsonify({"error": "Formato de mes inválido. Use YYYY-MM"}), 400
            
            # Ordenar por fecha y turno
            query = query.order_by(HorarioMedico.fecha, HorarioMedico.turno)
            
            # Ejecutar consulta
            resultados = query.all()
            
            # Construir respuesta
            resultado = []
            for horario, citas_activas in resultados:
                horario_dict = horario.to_dict()
                horario_dict['cupos_disponibles'] = horario.cupos - citas_activas
                resultado.append(horario_dict)
            
            return jsonify(resultado), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @staticmethod
    def get_horarios_resumen_mes():
        """
        Obtiene un resumen de horarios agrupado por día para un mes específico.
        Útil para mostrar en el calendario del frontend.
        
        Query params:
        - medico_id: (requerido) ID del médico
        - mes: (requerido) Mes en formato YYYY-MM
        """
        try:
            medico_id = request.args.get('medico_id')
            mes = request.args.get('mes')
            
            if not medico_id or not mes:
                return jsonify({"error": "Se requiere medico_id y mes"}), 400
            
            try:
                year, month = map(int, mes.split("-"))
                fecha_inicio = date(year, month, 1)
                _, dias_en_mes = monthrange(year, month)
                fecha_fin = date(year, month, dias_en_mes)
            except ValueError:
                return jsonify({"error": "Formato de mes inválido. Use YYYY-MM"}), 400
            
            horarios = HorarioMedico.query.filter(
                HorarioMedico.medico_id == medico_id,
                HorarioMedico.fecha >= fecha_inicio,
                HorarioMedico.fecha <= fecha_fin
            ).order_by(HorarioMedico.fecha, HorarioMedico.turno).all()
            
            # Agrupar por fecha
            resumen = {}
            for h in horarios:
                fecha_str = str(h.fecha)
                if fecha_str not in resumen:
                    resumen[fecha_str] = {
                        "fecha": fecha_str,
                        "dia_semana": h.dia_semana,
                        "turnos": {}
                    }
                resumen[fecha_str]["turnos"][h.turno] = {
                    "id": h.id,
                    "turno": h.turno,
                    "turno_nombre": h.turno_nombre,
                    "hora_inicio": str(h.hora_inicio),
                    "hora_fin": str(h.hora_fin),
                    "cupos": h.cupos,
                    "area_id": h.area_id,
                    "area_nombre": h.area_nombre
                }
            
            return jsonify({
                "medico_id": int(medico_id),
                "mes": mes,
                "dias": list(resumen.values())
            }), 200
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @staticmethod
    def delete_horario(id):
        """Elimina un horario específico por ID"""
        try:
            horario = HorarioMedico.query.get(id)
            if not horario:
                return jsonify({"error": "Horario no encontrado"}), 404
            
            db.session.delete(horario)
            db.session.commit()
            return jsonify({"message": "Horario eliminado correctamente"}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500

    @staticmethod
    def delete_horarios_mes():
        """
        Elimina todos los horarios de un médico para un mes específico.
        
        Query params:
        - medico_id: (requerido) ID del médico
        - mes: (requerido) Mes en formato YYYY-MM
        - turno: (opcional) 'M' o 'T' para eliminar solo un turno
        """
        try:
            medico_id = request.args.get('medico_id')
            mes = request.args.get('mes')
            turno = request.args.get('turno')
            
            if not medico_id or not mes:
                return jsonify({"error": "Se requiere medico_id y mes"}), 400
            
            try:
                year, month = map(int, mes.split("-"))
                fecha_inicio = date(year, month, 1)
                _, dias_en_mes = monthrange(year, month)
                fecha_fin = date(year, month, dias_en_mes)
            except ValueError:
                return jsonify({"error": "Formato de mes inválido. Use YYYY-MM"}), 400
            
            query = HorarioMedico.query.filter(
                HorarioMedico.medico_id == medico_id,
                HorarioMedico.fecha >= fecha_inicio,
                HorarioMedico.fecha <= fecha_fin
            )
            
            if turno:
                query = query.filter_by(turno=turno)
            
            deleted_count = query.delete()
            db.session.commit()
            
            return jsonify({
                "message": f"{deleted_count} horarios eliminados correctamente",
                "eliminados": deleted_count
            }), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500

    # Métodos legacy mantenidos por compatibilidad
    @staticmethod
    def get_horarios_by_medico(medico_id):
        return HorarioController.get_horarios_internal(medico_id=medico_id)

    @staticmethod
    def get_horarios_by_area(area_id):
        return HorarioController.get_horarios_internal(area_id=area_id)

    @staticmethod
    def get_horarios_internal(medico_id=None, area_id=None):
        try:
            query = HorarioMedico.query
            if medico_id:
                query = query.filter_by(medico_id=medico_id)
            if area_id:
                query = query.filter_by(area_id=area_id)
            query = query.order_by(HorarioMedico.fecha, HorarioMedico.turno)
            horarios = query.all()
            return jsonify([h.to_dict() for h in horarios]), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
