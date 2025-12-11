from flask import jsonify
from extensions.database import db
from models.area_model import Area
from services.gemini_services import GeminiService

class AreaController:

    @staticmethod
    def get_all():
        try:
            areas = Area.query.order_by(Area.id.desc()).all()
            return jsonify([area.to_dict() for area in areas]), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @staticmethod
    def create(data):
        try:
            nombre = data.get("nombre")
            if not nombre:
                return jsonify({"error": "El nombre es obligatorio"}), 400

            existing = Area.query.filter_by(nombre=nombre).first()
            if existing:
                return jsonify({"error": "El nombre del área ya existe"}), 409

            nueva_area = Area(
                nombre=nombre,
                descripcion=data.get("descripcion"),
                activo=data.get("activo", True)
            )

            db.session.add(nueva_area)
            db.session.commit()

            return jsonify({
                "message": "Área creada correctamente",
                "data": nueva_area.to_dict()
            }), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500

    @staticmethod
    def update(id, data):
        try:
            area = Area.query.get(id)
            if not area:
                return jsonify({"error": "Área no encontrada"}), 404

            if "nombre" in data:
                existing = Area.query.filter_by(nombre=data["nombre"]).first()
                if existing and existing.id != id:
                    return jsonify({"error": "El nombre del área ya existe"}), 409
                area.nombre = data["nombre"]

            if "descripcion" in data:
                area.descripcion = data["descripcion"]
            
            if "activo" in data:
                area.activo = data["activo"]

            db.session.commit()

            return jsonify({
                "message": "Área actualizada correctamente",
                "data": area.to_dict()
            }), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500

    @staticmethod
    def delete(id):
        try:
            area = Area.query.get(id)
            if not area:
                return jsonify({"error": "Área no encontrada"}), 404

            db.session.delete(area)
            db.session.commit()

            return jsonify({"message": "Área eliminada correctamente"}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500
    @staticmethod
    def recommend(data):
        try:
            sintomas = data.get("sintomas")
            if not sintomas:
                return jsonify({"error": "Debe proporcionar los síntomas del paciente"}), 400
            
            # Obtener todas las áreas activas
            areas = Area.query.filter_by(activo=True).all()
            if not areas:
                return jsonify({"error": "No hay áreas disponibles para recomendar"}), 404
                
            areas_list = [a.to_dict() for a in areas]
            
            recommendation = GeminiService.recommend_area(sintomas, areas_list)
            
            if "error" in recommendation:
                return jsonify(recommendation), 500 if "status" not in recommendation else recommendation["status"]
                
            return jsonify(recommendation), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
