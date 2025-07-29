import sqlite3
import os

# Cambiar al directorio del script
os.chdir(r'C:\xampp\htdocs\Proyecto_Gastro\foodtrail_sucre\foodtrail_project')

# Conectar a la base de datos
conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

try:
    # Obtener todas las tablas del chatbot
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'chatbot_%'")
    tables = cursor.fetchall()
    
    print('Tablas del chatbot encontradas:')
    for table in tables:
        print(f'  - {table[0]}')
    
    # Eliminar todas las tablas del chatbot
    for table in tables:
        cursor.execute(f'DROP TABLE IF EXISTS "{table[0]}"')
        print(f'Eliminada tabla: {table[0]}')
    
    # Eliminar también registros de migración del chatbot
    cursor.execute("DELETE FROM django_migrations WHERE app = 'chatbot'")
    deleted_migrations = cursor.rowcount
    print(f'Eliminados {deleted_migrations} registros de migración del chatbot')
    
    conn.commit()
    print('¡Limpieza completada exitosamente!')
    
except Exception as e:
    print(f'Error: {e}')
    conn.rollback()
    
finally:
    conn.close()
