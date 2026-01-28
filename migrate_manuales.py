"""
Script de migración para guardar los manuales de usuario.
"""
from app import app
from extensions.database import db
from sqlalchemy import text

def run_migration():
    print("=" * 60)
    print("  MIGRACIÓN: Crear tabla 'manuales'")
    print("=" * 60)
    
    with app.app_context():
        try:
            # Crear tabla manuales
            sql = """
            CREATE TABLE IF NOT EXISTS manuales (
                id SERIAL PRIMARY KEY,
                nombre VARCHAR(100) NOT NULL,
                descripcion TEXT,
                url_drive TEXT NOT NULL,
                rol_id INTEGER REFERENCES roles(id),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
            
            db.session.execute(text(sql))
            db.session.commit()
            print("✓ Tabla 'manuales' creada o ya existente.")
            
            # Mostrar estructura actualizada
            result = db.session.execute(text("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = 'manuales'
                ORDER BY ordinal_position
            """))
            
            print("\nEstructura actual de la tabla 'manuales':")
            print("-" * 50)
            for row in result:
                print(f"  {row[0]:25} | {row[1]:15} | {'NULL' if row[2] == 'YES' else 'NOT NULL'}")
                
        except Exception as e:
            db.session.rollback()
            print(f"\n✗ Error en migración: {e}")
            raise

if __name__ == "__main__":
    run_migration()
