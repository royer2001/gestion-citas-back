from app import app, db
from sqlalchemy import text

with app.app_context():
    try:
        # Verificar estado actual
        print("Estado actual de roles:")
        with db.engine.connect() as connection:
            result = connection.execute(text("SELECT * FROM roles WHERE id=2"))
            for row in result:
                print(row)

        # Actualizar rol
        sql = text("UPDATE roles SET nombre = 'profesional' WHERE id = 2")
        db.session.execute(sql)
        db.session.commit()
        print("\n✅ Rol actualizado a 'profesional'")
        
        # Verificar cambios
        print("\nNuevo estado de roles:")
        with db.engine.connect() as connection:
            result = connection.execute(text("SELECT * FROM roles WHERE id=2"))
            for row in result:
                print(row)
                
    except Exception as e:
        print(f"Error: {e}")
        db.session.rollback()
