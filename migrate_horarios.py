"""
Script para migrar la tabla horarios_medicos al nuevo esquema con turnos.

IMPORTANTE: Este script eliminará los datos existentes en horarios_medicos.
Ejecutar solo una vez después de actualizar el modelo.

Uso: python migrate_horarios.py
"""
from app import app, db
from models.horario_medico_model import HorarioMedico

def migrate():
    with app.app_context():
        # Eliminar tabla existente si causa conflictos
        try:
            # Intentar eliminar la tabla existente
            HorarioMedico.__table__.drop(db.engine, checkfirst=True)
            print("✓ Tabla anterior eliminada")
        except Exception as e:
            print(f"Nota: {e}")
        
        # Crear tabla con nuevo esquema
        db.create_all()
        print("✓ Tabla horarios_medicos creada con nuevo esquema")
        print("\nNuevo esquema:")
        print("  - id (Integer, PK)")
        print("  - medico_id (FK usuarios.id)")
        print("  - area_id (FK areas.id)")
        print("  - fecha (Date) - Fecha específica")
        print("  - dia_semana (Integer) - 0=Lun...6=Dom")
        print("  - turno (String) - 'M'=Mañana, 'T'=Tarde")
        print("  - cupos (Integer)")
        print("\nHorarios fijos:")
        print("  - Mañana: 07:30 - 13:30")
        print("  - Tarde:  13:30 - 19:30")

if __name__ == "__main__":
    migrate()
