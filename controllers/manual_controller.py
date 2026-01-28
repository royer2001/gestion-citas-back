from flask import jsonify, request
from extensions.database import db
from models.manual_model import Manual
from models.rol_model import Rol

def get_manuales():
    try:
        manuales = Manual.query.all()
        return jsonify([m.to_dict() for m in manuales]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def get_manuales_por_rol(rol_id):
    try:
        # Si rol_id es 0 o 'all', devuelve todos, o implementa lógica según necesidad
        if rol_id is None:
             return get_manuales()
             
        manuales = Manual.query.filter((Manual.rol_id == rol_id) | (Manual.rol_id == None)).all()
        return jsonify([m.to_dict() for m in manuales]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def create_manual():
    try:
        data = request.json
        nombre = data.get('nombre')
        url_drive = data.get('url_drive')
        descripcion = data.get('descripcion')
        rol_id = data.get('rol_id')

        if not nombre or not url_drive:
            return jsonify({"error": "Nombre y URL son requeridos"}), 400

        nuevo_manual = Manual(
            nombre=nombre,
            url_drive=url_drive,
            descripcion=descripcion,
            rol_id=rol_id
        )

        db.session.add(nuevo_manual)
        db.session.commit()

        return jsonify({
            "message": "Manual creado exitosamente",
            "manual": nuevo_manual.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

def update_manual(id):
    try:
        manual = Manual.query.get(id)
        if not manual:
            return jsonify({"error": "Manual no encontrado"}), 404

        data = request.json
        if 'nombre' in data:
            manual.nombre = data['nombre']
        if 'url_drive' in data:
            manual.url_drive = data['url_drive']
        if 'descripcion' in data:
            manual.descripcion = data['descripcion']
        if 'rol_id' in data:
            manual.rol_id = data['rol_id']

        db.session.commit()
        return jsonify({
            "message": "Manual actualizado exitosamente",
            "manual": manual.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

def delete_manual(id):
    try:
        manual = Manual.query.get(id)
        if not manual:
            return jsonify({"error": "Manual no encontrado"}), 404

        db.session.delete(manual)
        db.session.commit()
        return jsonify({"message": "Manual eliminado exitosamente"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
