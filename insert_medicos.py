"""
Script para insertar 5 médicos de prueba
"""
from app import app, db
from models.usuario_model import Usuario
from werkzeug.security import generate_password_hash

medicos = [
    {
        "dni": "12345678",
        "username": "jperez",
        "password": generate_password_hash("medico123"),
        "nombres_completos": "Dr. Juan Carlos Pérez Mendoza",
        "rol_id": 2,  # 2 = medico
        "activo": True
    },
    {
        "dni": "23456789",
        "username": "mgarcia",
        "password": generate_password_hash("medico123"),
        "nombres_completos": "Dra. María Elena García Torres",
        "rol_id": 2,  # 2 = medico
        "activo": True
    },
    {
        "dni": "34567890",
        "username": "rlopez",
        "password": generate_password_hash("medico123"),
        "nombres_completos": "Dr. Roberto Andrés López Vargas",
        "rol_id": 2,  # 2 = medico
        "activo": True
    },
    {
        "dni": "45678901",
        "username": "acastillo",
        "password": generate_password_hash("medico123"),
        "nombres_completos": "Dra. Ana Lucía Castillo Ramos",
        "rol_id": 2,  # 2 = medico
        "activo": True
    },
    {
        "dni": "56789012",
        "username": "frodriguez",
        "password": generate_password_hash("medico123"),
        "nombres_completos": "Dr. Fernando José Rodríguez Silva",
        "rol_id": 2,  # 2 = medico
        "activo": True
    }
]

def insertar_medicos():
    with app.app_context():
        insertados = 0
        for medico_data in medicos:
            # Verificar si ya existe por DNI
            existente = Usuario.query.filter_by(dni=medico_data["dni"]).first()
            if existente:
                print(f"⚠️  Médico con DNI {medico_data['dni']} ya existe: {existente.nombres_completos}")
                continue
            
            medico = Usuario(**medico_data)
            db.session.add(medico)
            insertados += 1
            print(f"✅ Insertado: {medico_data['nombres_completos']}")
        
        db.session.commit()
        print(f"\n{'='*50}")
        print(f"Total insertados: {insertados} médicos")
        print(f"Contraseña para todos: medico123")

if __name__ == "__main__":
    insertar_medicos()
