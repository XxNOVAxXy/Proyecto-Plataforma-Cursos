from flask import Flask

# --- 1. Importación de todos los Blueprints ---
# Importamos cada "mini-app" desde su archivo correspondiente en la carpeta 'routes'.
from routes.instructores import instructores_bp
from routes.cursos import cursos_bp
from routes.modulos import modulos_bp
from routes.lecciones import lecciones_bp

# --- 2. Creación de la Aplicación Principal ---
# Esta es la instancia principal de nuestra aplicación Flask.
app = Flask(__name__)

# --- 3. Registro de Blueprints en la Aplicación ---
# Aquí le decimos a nuestra aplicación principal que "active" cada mini-app
# y le asignamos un prefijo de URL a cada una.
# Esto mantiene nuestro código organizado.

# Todas las rutas definidas en 'instructores.py' empezarán con /api/instructors
app.register_blueprint(instructores_bp, url_prefix='/api/instructors')

# Todas las rutas definidas en 'cursos.py' empezarán con /api/courses
app.register_blueprint(cursos_bp, url_prefix='/api/courses')

# Todas las rutas definidas en 'modulos.py' empezarán con /api/modules
app.register_blueprint(modulos_bp, url_prefix='/api/modules')

# Todas las rutas definidas en 'lecciones.py' empezarán con /api/lessons
app.register_blueprint(lecciones_bp, url_prefix='/api/lessons')


# --- 4. Punto de Entrada para Ejecutar el Servidor ---
# Este bloque de código se asegura de que el servidor se inicie solo
# cuando ejecutamos este archivo directamente (con 'python app.py').
if __name__ == "__main__":
    # app.run() inicia el servidor de desarrollo.
    # debug=True es muy útil durante el desarrollo porque:
    #   1. Reinicia el servidor automáticamente cada vez que guardas un cambio en un archivo.
    #   2. Muestra errores detallados en el navegador si algo sale mal.
    app.run(debug=True, port=5000)