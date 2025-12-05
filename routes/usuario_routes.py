from flask import Blueprint, request
from controllers.usuario_controller import UsuarioController
from middleware.auth_middleware import token_required, roles_required
from extensions.jwt_manager import JWTManager
from flask import jsonify


usuario_bp = Blueprint("usuario_bp", __name__)

# CREATE
@usuario_bp.post("/create")
def crear_usuario():
    data = request.get_json()
    return UsuarioController.crear_usuario(data)


# LOGIN
@usuario_bp.post("/login")
def login():
    data = request.get_json()
    return UsuarioController.login(data)

# REFRESH
@usuario_bp.post("/refresh")
def refresh():
    refresh_token = request.cookies.get("refresh_token")

    if not refresh_token:
        return jsonify({"error": "No hay refresh token"}), 401

    decoded = JWTManager.decode_token(refresh_token)

    if "error" in decoded:
        return jsonify(decoded), 401

    user_data = decoded["data"]

    new_access = JWTManager.create_access_token(user_data)

    return jsonify({"access_token": new_access})


# EJEMPLO DE RUTA PROTEGIDA
@usuario_bp.get("/perfil")
@token_required
def perfil():
    return {"user": request.user}, 200


# EJEMPLO RUTA SOLO ADMIN
@usuario_bp.get("/admin-only")
@token_required
@roles_required("administrador")
def admin_only():
    return {"message": "Bienvenido administrador"}, 200

@usuario_bp.post("/logout")
def logout():
    response = jsonify({"message": "Sesión cerrada"})
    response.set_cookie("refresh_token", "", expires=0)
    return response


@usuario_bp.get("/medicos")
@token_required
def get_medicos():
    return UsuarioController.get_medicos()

