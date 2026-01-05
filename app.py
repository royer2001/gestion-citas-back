from dotenv import load_dotenv
load_dotenv()

import os
from flask import Flask, jsonify
from routes.paciente_route import paciente_bp
from routes.dni_routes import dni_bp
from routes.usuario_routes import usuario_bp
from routes.area_routes import area_bp
from routes.cita_routes import cita_bp
from routes.horario_routes import horario_bp
from routes.dashboard_routes import dashboard_bp
from routes.medico_routes import medico_bp  # Nuevo import para medicos
from routes.indicador_routes import indicador_bp  # Import para indicadores de tesis
from config import SQLALCHEMY_DATABASE_URI, SQLALCHEMY_TRACK_MODIFICATIONS
from extensions.database import db
from flask_cors import CORS

app = Flask(__name__)

# SECRET KEY para JWT (desde variable de entorno en producción)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "super_clave_secreta_desarrollo")

# DB config
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = SQLALCHEMY_TRACK_MODIFICATIONS

# Configuración optimizada para Supabase/Railway (evita errores de conexión perdida y límite de clientes)
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_size': 5,                # Mantener máximo 5 conexiones abiertas
    'max_overflow': 2,             # Permitir solo 2 conexiones extra temporales
    'pool_recycle': 300,           # Reciclar conexiones cada 5 minutos
    'pool_pre_ping': True,         # Verificar conexión antes de usarla
    'pool_timeout': 30             # Tiempo máximo de espera por una conexión
}

# CORS - Configuración dinámica para desarrollo y producción
frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
allowed_origins = [frontend_url]

# Si hay múltiples orígenes separados por coma, los parseamos
if "," in frontend_url:
    allowed_origins = [url.strip() for url in frontend_url.split(",")]

# En desarrollo, permitir localhost
if os.getenv("FLASK_ENV") != "production":
    allowed_origins.extend([
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ])
    # Eliminar duplicados
    allowed_origins = list(set(allowed_origins))

CORS(app,
     origins=allowed_origins,
     supports_credentials=True,
     allow_headers=["Content-Type", "Authorization"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
)

# Inicializar DB
db.init_app(app)

# ==================== RUTAS DE SALUD ====================
@app.route('/api/health', methods=['GET'])
def health_check():
    """Endpoint de salud para Railway healthcheck"""
    return jsonify({
        "status": "healthy",
        "message": "API Citas Médicas funcionando correctamente"
    }), 200

@app.route('/', methods=['GET'])
def root():
    """Endpoint raíz para verificar que el servidor está corriendo"""
    return jsonify({
        "message": "API Citas Médicas - Centro de Salud La Unión",
        "version": "1.0.0",
        "docs": "/api/health"
    }), 200

# Rutas API (ahora con prefijo /api)
app.register_blueprint(paciente_bp, url_prefix="/api/pacientes")
app.register_blueprint(dni_bp, url_prefix="/api/dni")
app.register_blueprint(usuario_bp, url_prefix="/api/auth")
app.register_blueprint(area_bp, url_prefix="/api/areas")
app.register_blueprint(cita_bp, url_prefix="/api/citas")
app.register_blueprint(horario_bp, url_prefix="/api/horarios")
app.register_blueprint(dashboard_bp, url_prefix="/api/dashboard")
app.register_blueprint(medico_bp, url_prefix="/api/medicos")
app.register_blueprint(indicador_bp, url_prefix="/api/indicadores")  # Indicadores para tesis

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    
    # Puerto dinámico para Railway
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_ENV") != "production"
    
    app.run(host="0.0.0.0", port=port, debug=debug)

