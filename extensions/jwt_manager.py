import jwt
from datetime import datetime, timedelta
from flask import current_app


class JWTManager:

    @staticmethod
    def create_access_token(data, expires_minutes=15):
        payload = {
            "exp": datetime.utcnow() + timedelta(minutes=expires_minutes),
            "iat": datetime.utcnow(),
            "type": "access",
            "data": data
        }
        token = jwt.encode(
            payload, current_app.config["SECRET_KEY"], algorithm="HS256")
        return token

    @staticmethod
    def create_refresh_token(data, expires_days=7):
        payload = {
            "exp": datetime.utcnow() + timedelta(days=expires_days),
            "iat": datetime.utcnow(),
            "type": "refresh",
            "data": data
        }
        token = jwt.encode(
            payload, current_app.config["SECRET_KEY"], algorithm="HS256")
        return token

    @staticmethod
    def decode_token(token):
        try:
            return jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return {"error": "Token expirado"}
        except jwt.InvalidTokenError:
            return {"error": "Token inválido"}
