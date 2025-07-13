# seed.py
from faker import Faker
import random
from conexion import get_db_connection # Reutilizamos nuestra función de conexión

# Inicializamos Faker para generar datos en español
fake = Faker('es_ES')

def seed_database(count=100):
    """
    Puebla la base de datos con una cantidad específica de registros de prueba.
    """
    conn = get_db_connection()
    if not conn:
        print("No se pudo conectar a la base de datos. Saliendo del script de seeding.")
        return
        
    cursor = conn.cursor()
    print("Conexión exitosa. Iniciando el proceso de seeding...")

    try:
        # --- 1. Generar e Insertar Instructores ---
        instructores = []
        for _ in range(count):
            instructores.append((fake.name(), fake.unique.email()))
        
        cursor.executemany("INSERT INTO instructores (nombre, email) VALUES (%s, %s)", instructores)
        print(f"-> {cursor.rowcount} instructores insertados.")

        # --- 2. Generar e Insertar Cursos ---
        # Primero, obtenemos los IDs de los instructores que acabamos de crear
        cursor.execute("SELECT id FROM instructores")
        instructor_ids = [item[0] for item in cursor.fetchall()]
        
        cursos = []
        for _ in range(count):
            cursos.append((
                fake.catch_phrase(), # Genera una frase llamativa como título
                fake.text(max_nb_chars=300),
                random.choice([True, False]), # Publicado o no al azar
                random.choice(instructor_ids) # Asigna un instructor al azar
            ))
        cursor.executemany("INSERT INTO cursos (titulo, descripcion, is_published, instructor_id) VALUES (%s, %s, %s, %s)", cursos)
        print(f"-> {cursor.rowcount} cursos insertados.")

        # --- 3. Generar e Insertar Módulos ---
        cursor.execute("SELECT id FROM cursos")
        curso_ids = [item[0] for item in cursor.fetchall()]

        modulos = []
        for curso_id in curso_ids:
            # Crear entre 2 y 5 módulos por curso
            for i in range(random.randint(2, 5)):
                modulos.append((f"Módulo {i+1}: {fake.sentence(nb_words=4)}", curso_id))
        
        cursor.executemany("INSERT INTO modulos (titulo, curso_id) VALUES (%s, %s)", modulos)
        print(f"-> {cursor.rowcount} módulos insertados.")
        
        # --- 4. Generar e Insertar Lecciones ---
        cursor.execute("SELECT id FROM modulos")
        modulo_ids = [item[0] for item in cursor.fetchall()]
        
        lecciones = []
        for modulo_id in modulo_ids:
            # Crear entre 3 y 8 lecciones por módulo
            for i in range(random.randint(3, 8)):
                lecciones.append((f"Lección {i+1}: {fake.sentence(nb_words=6)}", fake.text(max_nb_chars=500), modulo_id))
        
        cursor.executemany("INSERT INTO lecciones (titulo, contenido, modulo_id) VALUES (%s, %s, %s)", lecciones)
        print(f"-> {cursor.rowcount} lecciones insertadas.")

        # Confirmar todos los cambios en la base de datos
        conn.commit()
        print("\n¡Seeding completado exitosamente! Todos los cambios han sido guardados.")

    except Exception as e:
        print(f"\nOcurrió un error durante el seeding: {e}")
        conn.rollback() # Revertir cambios si algo sale mal
    finally:
        # Cerrar la conexión
        cursor.close()
        conn.close()
        print("Conexión con la base de datos cerrada.")

# Esto hace que el script se ejecute solo cuando lo llamas directamente
if __name__ == '__main__':
    seed_database()