from flask import Blueprint, request, jsonify
# Importa la función de conexión desde la raíz del proyecto
from conexion import get_db_connection

# Crea el Blueprint para los instructores
instructores_bp = Blueprint('instructores_bp', __name__)

# --- ENDPOINT 1: OBTENER TODOS LOS INSTRUCTORES ---
@instructores_bp.route('/', methods=['GET'])
def get_instructores():
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Error de conexión a la base de datos"}), 500
        
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM instructores ORDER BY id ASC")
        instructores = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify(instructores)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- ENDPOINT 2: OBTENER UN SOLO INSTRUCTOR POR ID ---
@instructores_bp.route('/<int:id>', methods=['GET'])
def get_instructor(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM instructores WHERE id = %s", (id,))
        instructor = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if instructor:
            return jsonify(instructor)
        else:
            return jsonify({"error": "Instructor no encontrado"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- ENDPOINT 3: CREAR UN NUEVO INSTRUCTOR ---
@instructores_bp.route('/', methods=['POST'])
def crear_instructor():
    # Obtiene los datos del cuerpo de la solicitud en formato JSON
    data = request.get_json()
    nombre = data.get('nombre')
    email = data.get('email')

    # Validación simple
    if not nombre or not email:
        return jsonify({"error": "Nombre y email son campos requeridos"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Se inserta el nuevo instructor en la base de datos
        cursor.execute("INSERT INTO instructores (nombre, email) VALUES (%s, %s)", (nombre, email))
        conn.commit()
        
        # Obtenemos el ID del nuevo instructor creado
        nuevo_id = cursor.lastrowid
        
        cursor.close()
        conn.close()
        
        # Devolvemos un mensaje de éxito y el ID del nuevo instructor
        return jsonify({"message": "Instructor creado exitosamente", "id": nuevo_id}), 201
    except Exception as e:
        # Manejo de error de email duplicado
        if 'Duplicate entry' in str(e):
            return jsonify({"error": "El email ya está registrado"}), 409
        return jsonify({"error": str(e)}), 500

# --- ENDPOINT 4: ACTUALIZAR UN INSTRUCTOR EXISTENTE ---
@instructores_bp.route('/<int:id>', methods=['PUT'])
def actualizar_instructor(id):
    data = request.get_json()
    nombre = data.get('nombre')
    email = data.get('email')

    if not nombre and not email:
        return jsonify({"error": "Se requiere al menos un campo (nombre o email) para actualizar"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Construcción de la consulta SQL dinámicamente
        query_parts = []
        params = []
        if nombre:
            query_parts.append("nombre = %s")
            params.append(nombre)
        if email:
            query_parts.append("email = %s")
            params.append(email)
        
        params.append(id)
        
        query = f"UPDATE instructores SET {', '.join(query_parts)} WHERE id = %s"
        
        cursor.execute(query, tuple(params))
        conn.commit()
        
        # Verificamos si se actualizó alguna fila
        if cursor.rowcount == 0:
            cursor.close()
            conn.close()
            return jsonify({"error": "Instructor no encontrado"}), 404
            
        cursor.close()
        conn.close()
        
        return jsonify({"message": "Instructor actualizado exitosamente"}), 200
    except Exception as e:
        if 'Duplicate entry' in str(e):
            return jsonify({"error": "El email ya está en uso por otro instructor"}), 409
        return jsonify({"error": str(e)}), 500

# --- ENDPOINT 5: ELIMINAR UN INSTRUCTOR (CON REGLA DE NEGOCIO) ---
@instructores_bp.route('/<int:id>', methods=['DELETE'])
def eliminar_instructor(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # REGLA DE NEGOCIO CRÍTICA: No se puede eliminar un instructor con cursos públicos.
        # Primero, contamos cuántos cursos publicados tiene este instructor.
        cursor.execute("SELECT COUNT(*) as conteo FROM cursos WHERE instructor_id = %s AND is_published = TRUE", (id,))
        resultado = cursor.fetchone()
        
        if resultado['conteo'] > 0:
            cursor.close()
            conn.close()
            # Si tiene cursos publicados, se prohíbe la eliminación.
            return jsonify({"error": f"No se puede eliminar. El instructor tiene {resultado['conteo']} curso(s) publicado(s)."}), 409 # 409 Conflict
            
        # Si no tiene cursos publicados, procedemos a eliminarlo.
        # La BD se encargará de poner instructor_id = NULL en los cursos no publicados gracias a ON DELETE SET NULL.
        cursor.execute("DELETE FROM instructores WHERE id = %s", (id,))
        conn.commit()
        
        if cursor.rowcount == 0:
            cursor.close()
            conn.close()
            return jsonify({"error": "Instructor no encontrado"}), 404
            
        cursor.close()
        conn.close()
        
        return jsonify({"message": "Instructor eliminado exitosamente"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500