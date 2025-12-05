from flask import jsonify, request
from werkzeug.security import generate_password_hash, check_password_hash
from extensions.database import db
from models.usuario_model import Usuario
from models.horario_medico_model import HorarioMedico
from extensions.jwt_manager import JWTManager
from flask import make_response


class UsuarioController:

    @staticmethod
    def crear_usuario(data):
        try:
            required = ["dni", "password", "rol_id"]
            for field in required:
                if field not in data or not data[field]:
                    return jsonify({"error": f"El campo '{field}' es obligatorio"}), 400

            # Verificar usuario existente
            if Usuario.query.filter_by(dni=data["dni"]).first():
                return jsonify({"error": "El dni ya está registrado"}), 409

            usuario = Usuario(
                dni=data["dni"],
                password=generate_password_hash(data["password"]),
                rol_id=data["rol_id"],
                nombres_completos=data.get("nombres_completos")
            )

            db.session.add(usuario)
            db.session.commit()

            return jsonify({
                "message": "Usuario creado correctamente",
                "usuario": usuario.to_dict()
            }), 201

        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500

    @staticmethod
    def login(data):
        dni = data.get("dni")
        password = data.get("password")

        if not dni or not password:
            return jsonify({"error": "dni y password son requeridos"}), 400

        usuario = Usuario.query.filter_by(dni=dni).first()

        if not usuario:
            return jsonify({"error": "Credenciales incorrectas"}), 401

        if not check_password_hash(usuario.password, password):
            return jsonify({"error": "Credenciales incorrectas"}), 401

        access = JWTManager.create_access_token({
            "id": usuario.id,
            "dni": usuario.dni,
            "rol_id": usuario.rol_id
        })

        response = make_response({
            "message": "Login exitoso",
            "access_token": access,
            "usuario": usuario.to_dict()
        })

        # Guardar refresh token como cookie HTTP-Only
        response.set_cookie(
            "refresh_token",
            JWTManager.create_refresh_token({
                "id": usuario.id,
                "dni": usuario.dni,
                "rol_id": usuario.rol_id
            }),
            httponly=True,
            secure=False,  # Cambiar a True en producción HTTPS
            samesite="Strict",
            max_age=60*60*24*7  # 7 días
        )

        return response

    @staticmethod
    def refresh_token(data):
        refresh_token = data.get("refresh_token")

        if not refresh_token:
            return jsonify({"error": "refresh_token requerido"}), 400

        decoded = JWTManager.decode_token(refresh_token)

        if "error" in decoded:
            return jsonify(decoded), 401

        if decoded.get("type") != "refresh":
            return jsonify({"error": "Token no es de tipo refresh"}), 401

        user_data = decoded["data"]

        new_access = JWTManager.create_access_token(user_data)

        return jsonify({"access_token": new_access})

    @staticmethod
    def get_medicos():
        try:
            area_id = request.args.get('area_id')
            query = Usuario.query.filter_by(rol_id=2)

            if area_id:
                # Filtrar médicos que tienen horarios en esa área
                medicos_con_horario = db.session.query(HorarioMedico.medico_id).filter_by(area_id=area_id).distinct().all()
                medico_ids = [m[0] for m in medicos_con_horario]
                query = query.filter(Usuario.id.in_(medico_ids))

            medicos = query.all()
            return jsonify([m.to_dict() for m in medicos]), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
