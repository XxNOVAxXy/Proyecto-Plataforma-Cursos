from flask import Blueprint, request, jsonify
from conexion import get_db_connection

lecciones_bp = Blueprint('lecciones_bp', __name__)

# --- Función Auxiliar ---
def check_curso_publicado_por_leccion(leccion_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT c.is_published
        FROM cursos c
        JOIN modulos m ON c.id = m.curso_id
        JOIN lecciones l ON m.id = l.modulo_id
        WHERE l.id = %s
    """, (leccion_id,))
    curso = cursor.fetchone()
    cursor.close()
    conn.close()
    return curso and curso['is_published']

# --- CRUD Básico para Lecciones Individuales ---
@lecciones_bp.route('/<int:id>', methods=['GET'])
def get_leccion(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM lecciones WHERE id = %s", (id,))
    leccion = cursor.fetchone()
    cursor.close()
    conn.close()
    return jsonify(leccion) if leccion else ({"error": "Lección no encontrada"}, 404)

@lecciones_bp.route('/<int:id>', methods=['PUT'])
def actualizar_leccion(id):
    if check_curso_publicado_por_leccion(id):
        return jsonify({"error": "No se puede editar una lección de un curso ya publicado"}), 403
    data = request.get_json()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE lecciones SET titulo = %s, contenido = %s WHERE id = %s", 
                   (data.get('titulo'), data.get('contenido'), id))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Lección actualizada"})

@lecciones_bp.route('/<int:id>', methods=['DELETE'])
def eliminar_leccion(id):
    if check_curso_publicado_por_leccion(id):
        return jsonify({"error": "No se puede eliminar una lección de un curso ya publicado"}), 403
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM lecciones WHERE id = %s", (id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Lección eliminada"})