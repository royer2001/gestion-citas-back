from functools import wraps
from flask import request, jsonify
from extensions.jwt_manager import JWTManager

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        token = None

        if "Authorization" in request.headers:
            token = request.headers["Authorization"].replace("Bearer ", "")

        if not token:
            return jsonify({"error": "Token no proporcionado"}), 401

        decoded = JWTManager.decode_token(token)

        if "error" in decoded:
            return jsonify(decoded), 401

        if decoded.get("type") != "access":
            return jsonify({"error": "Tipo de token inválido"}), 401

        request.user = decoded["data"]  # user info

        return f(*args, **kwargs)
    return decorated


def roles_required(*roles):
    def decorator(f):
        @wraps(f)
        def middleware(*args, **kwargs):
            if not hasattr(request, "user"):
                return jsonify({"error": "No autenticado"}), 403

            user_role = request.user.get("rol_id")

            if user_role not in roles:
                return jsonify({"error": "No autorizado"}), 403

            return f(*args, **kwargs)
        return middleware
    return decorator
