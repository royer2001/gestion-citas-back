from app import app, db
from sqlalchemy import inspect
from sqlalchemy import text

with app.app_context():
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    print("Tablas encontradas:", tables)
    
    if 'roles' in tables:
        print("\nContenido de tabla 'roles':")
        with db.engine.connect() as connection:
            result = connection.execute(text("SELECT * FROM roles"))
            for row in result:
                print(row)
    else:
        print("\nLa tabla 'roles' NO existe.")
