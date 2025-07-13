from flask import Blueprint, request, jsonify
from conexion import get_db_connection

# Creamos el Blueprint para las rutas que empiezan con /api/courses
cursos_bp = Blueprint('cursos_bp', __name__)

# --- Endpoint 1: OBTENER TODOS LOS CURSOS ---
# Ruta: GET /api/courses
@cursos_bp.route('/', methods=['GET'])
def get_cursos():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        # Usamos un LEFT JOIN para obtener también el nombre del instructor
        cursor.execute("""
            SELECT c.id, c.titulo, c.descripcion, c.is_published, c.instructor_id, i.nombre as instructor_nombre
            FROM cursos c
            LEFT JOIN instructores i ON c.instructor_id = i.id
            ORDER BY c.id ASC
        """)
        cursos = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(cursos)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- Endpoint 2: OBTENER UN SOLO CURSO POR ID ---
# Ruta: GET /api/courses/<id>
@cursos_bp.route('/<int:id>', methods=['GET'])
def get_curso(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        # Obtenemos el curso y también los módulos y lecciones que le pertenecen
        cursor.execute("""
            SELECT c.*, i.nombre as instructor_nombre
            FROM cursos c
            LEFT JOIN instructores i ON c.instructor_id = i.id
            WHERE c.id = %s
        """, (id,))
        curso = cursor.fetchone()

        if not curso:
            return jsonify({"error": "Curso no encontrado"}), 404

        # Obtenemos los módulos de este curso
        cursor.execute("SELECT * FROM modulos WHERE curso_id = %s ORDER BY id ASC", (id,))
        modulos = cursor.fetchall()
        
        # Para cada módulo, obtenemos sus lecciones
        for modulo in modulos:
            cursor.execute("SELECT * FROM lecciones WHERE modulo_id = %s ORDER BY id ASC", (modulo['id'],))
            lecciones = cursor.fetchall()
            modulo['lecciones'] = lecciones # Añadimos las lecciones al diccionario del módulo
        
        curso['modulos'] = modulos # Añadimos los módulos al diccionario del curso

        cursor.close()
        conn.close()
        return jsonify(curso)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- Endpoint 3: CREAR UN NUEVO CURSO ---
# Ruta: POST /api/courses
@cursos_bp.route('/', methods=['POST'])
def crear_curso():
    data = request.get_json()
    titulo = data.get('titulo')
    instructor_id = data.get('instructor_id')

    if not titulo or not instructor_id:
        return jsonify({"error": "Los campos 'titulo' e 'instructor_id' son requeridos"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO cursos (titulo, descripcion, instructor_id) VALUES (%s, %s, %s)", 
                       (titulo, data.get('descripcion'), instructor_id))
        conn.commit()
        nuevo_id = cursor.lastrowid
        cursor.close()
        conn.close()
        return jsonify({"message": "Curso creado exitosamente", "id": nuevo_id}), 201
    except Exception as e:
        # Manejo de error si el instructor_id no existe
        if 'foreign key constraint' in str(e).lower():
            return jsonify({"error": "El instructor_id proporcionado no existe."}), 404
        return jsonify({"error": str(e)}), 500

# --- Endpoint 4: ACTUALIZAR UN CURSO (CON REGLA DE NEGOCIO) ---
# Ruta: PUT /api/courses/<id>
@cursos_bp.route('/<int:id>', methods=['PUT'])
def actualizar_curso(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # REGLA DE NEGOCIO: No se puede editar un curso que ya está publicado.
        cursor.execute("SELECT is_published FROM cursos WHERE id = %s", (id,))
        curso = cursor.fetchone()

        if not curso:
            return jsonify({"error": "Curso no encontrado"}), 404
        if curso['is_published']:
            return jsonify({"error": "No se puede editar un curso que ya ha sido publicado"}), 403

        data = request.get_json()
        cursor.execute("UPDATE cursos SET titulo = %s, descripcion = %s, instructor_id = %s WHERE id = %s",
                       (data.get('titulo'), data.get('descripcion'), data.get('instructor_id'), id))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "Curso actualizado exitosamente"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- Endpoint 5: ELIMINAR UN CURSO (CON REGLA DE NEGOCIO) ---
# Ruta: DELETE /api/courses/<id>
@cursos_bp.route('/<int:id>', methods=['DELETE'])
def eliminar_curso(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT is_published FROM cursos WHERE id = %s", (id,))
        curso = cursor.fetchone()

        if not curso:
            return jsonify({"error": "Curso no encontrado"}), 404
        if curso['is_published']:
            return jsonify({"error": "No se puede eliminar un curso que ya ha sido publicado"}), 403

        cursor.execute("DELETE FROM cursos WHERE id = %s", (id,))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "Curso y todo su contenido (módulos y lecciones) han sido eliminados"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- Endpoint 6: PUBLICAR UN CURSO ---
# Ruta: POST /api/courses/<id>/publish
@cursos_bp.route('/<int:id>/publish', methods=['POST'])
def publicar_curso(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE cursos SET is_published = TRUE WHERE id = %s", (id,))
        conn.commit()
        
        if cursor.rowcount == 0:
            return jsonify({"error": "Curso no encontrado"}), 404
            
        cursor.close()
        conn.close()
        return jsonify({"message": "Curso publicado exitosamente"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- ENDPOINT 7: CREAR UN MÓDULO PARA UN CURSO (NUEVO) ---
# Ruta: POST /api/courses/<course_id>/modules
@cursos_bp.route('/<int:course_id>/modules', methods=['POST'])
def crear_modulo_para_curso(course_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # REGLA DE NEGOCIO: Verificar si el curso está publicado
        cursor.execute("SELECT is_published FROM cursos WHERE id = %s", (course_id,))
        curso = cursor.fetchone()

        if not curso:
            return jsonify({"error": "Curso no encontrado"}), 404
        if curso['is_published']:
            return jsonify({"error": "No se pueden añadir módulos a un curso ya publicado"}), 403

        data = request.get_json()
        titulo = data.get('titulo')
        if not titulo:
            return jsonify({"error": "El campo 'titulo' es requerido"}), 400

        cursor.execute("INSERT INTO modulos (titulo, curso_id) VALUES (%s, %s)", (titulo, course_id))
        conn.commit()
        nuevo_id = cursor.lastrowid
        cursor.close()
        conn.close()
        
        return jsonify({"message": "Módulo creado exitosamente", "id": nuevo_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500