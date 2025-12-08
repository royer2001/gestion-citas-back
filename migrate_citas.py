"""
Script de migración para agregar nuevos campos a la tabla 'citas'.

Nuevos campos:
- horario_id: FK a horarios_medicos
- area_id: FK a areas
- fecha: Fecha de la cita

Ejecutar:
    python migrate_citas.py
"""

from app import app
from extensions.database import db

MIGRATION_SQL = """
-- Agregar campo horario_id (FK a horarios_medicos)
ALTER TABLE citas ADD COLUMN IF NOT EXISTS horario_id INTEGER REFERENCES horarios_medicos(id);

-- Agregar campo area_id (FK a areas)
ALTER TABLE citas ADD COLUMN IF NOT EXISTS area_id INTEGER REFERENCES areas(id);

-- Agregar campo fecha (Date)
ALTER TABLE citas ADD COLUMN IF NOT EXISTS fecha DATE;

-- Hacer que el campo area sea nullable (ya no es obligatorio, se usa area_id)
ALTER TABLE citas ALTER COLUMN area DROP NOT NULL;

-- Agregar FK para doctor_id si no existe
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_name = 'citas_doctor_id_fkey'
    ) THEN
        ALTER TABLE citas ADD CONSTRAINT citas_doctor_id_fkey 
        FOREIGN KEY (doctor_id) REFERENCES usuarios(id);
    END IF;
EXCEPTION WHEN OTHERS THEN
    -- Ignorar si ya existe o hay error
    RAISE NOTICE 'FK doctor_id ya puede existir o error: %', SQLERRM;
END $$;
"""

def run_migration():
    print("=" * 60)
    print("  MIGRACIÓN: Actualizar tabla 'citas'")
    print("=" * 60)
    
    with app.app_context():
        try:
            # Ejecutar cada statement por separado
            statements = [
                "ALTER TABLE citas ADD COLUMN IF NOT EXISTS horario_id INTEGER REFERENCES horarios_medicos(id)",
                "ALTER TABLE citas ADD COLUMN IF NOT EXISTS area_id INTEGER REFERENCES areas(id)",
                "ALTER TABLE citas ADD COLUMN IF NOT EXISTS fecha DATE",
                "ALTER TABLE citas ALTER COLUMN area DROP NOT NULL",
            ]
            
            for stmt in statements:
                try:
                    db.session.execute(db.text(stmt))
                    print(f"✓ Ejecutado: {stmt[:60]}...")
                except Exception as e:
                    print(f"⚠ Advertencia en: {stmt[:40]}... - {str(e)[:50]}")
            
            db.session.commit()
            print("\n" + "=" * 60)
            print("  ✓ MIGRACIÓN COMPLETADA EXITOSAMENTE")
            print("=" * 60)
            
            # Mostrar estructura actualizada
            result = db.session.execute(db.text("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = 'citas'
                ORDER BY ordinal_position
            """))
            
            print("\nEstructura actual de la tabla 'citas':")
            print("-" * 50)
            for row in result:
                print(f"  {row[0]:25} | {row[1]:15} | {'NULL' if row[2] == 'YES' else 'NOT NULL'}")
            
        except Exception as e:
            db.session.rollback()
            print(f"\n✗ Error en migración: {e}")
            raise

if __name__ == "__main__":
    run_migration()
