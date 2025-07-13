import mysql.connector
from mysql.connector import Error

def get_db_connection():
    """
    Crea y retorna una conexión a la base de datos.
    Retorna el objeto de conexión si tiene éxito, o None si falla.
    """
    try:
        # --- ¡CONFIGURA TUS DATOS AQUÍ! ---
        # Reemplaza los valores si tu configuración de MySQL es diferente.
        conn = mysql.connector.connect(
            host='localhost',             # El servidor de tu base de datos, casi siempre 'localhost'
            user='root',                  # Tu nombre de usuario de MySQL (por defecto es 'root')
            password='',                  # Tu contraseña de MySQL (por defecto suele estar vacía)
            database='plataforma_cursos'  # El nombre de la base de datos que creamos
        )
        
        # Si la conexión fue exitosa, retorna el objeto de conexión
        return conn

    except Error as e:
        # Si ocurre un error durante la conexión, lo imprime en la consola
        print(f"Error al conectar a la base de datos MySQL: {e}")
        # Retorna None para indicar que la conexión falló
        return None