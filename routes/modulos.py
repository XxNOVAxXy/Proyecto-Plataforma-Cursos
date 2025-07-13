from flask import Blueprint, request, jsonify
from conexion import get_db_connection

modulos_bp = Blueprint('modulos_bp', __name__)

# --- Función Auxiliar ---
def check_curso_publicado(modulo_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT c.is_published FROM cursos c JOIN modulos m ON c.id = m.curso_id WHERE m.id = %s", (modulo_id,))
    curso = cursor.fetchone()
    cursor.close()
    conn.close()
    return curso and curso['is_published']

# --- CRUD Básico para Módulos Individuales ---
# ... (Aquí van los endpoints GET, PUT, DELETE para /modules/<id> que ya te di) ...

# --- ENDPOINT DE CREACIÓN DE LECCIONES ---
# Ruta: POST /api/modules/<module_id>/lessons
@modulos_bp.route('/<int:module_id>/lessons', methods=['POST'])
def crear_leccion_en_modulo(module_id):
    if check_curso_publicado(module_id):
        return jsonify({"error": "No se pueden añadir lecciones a un módulo de un curso ya publicado"}), 403

    data = request.get_json()
    titulo = data.get('titulo')
    if not titulo:
        return jsonify({"error": "El título es requerido"}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO lecciones (titulo, contenido, modulo_id) VALUES (%s, %s, %s)", 
                   (titulo, data.get('contenido'), module_id))
    conn.commit()
    nuevo_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return jsonify({"message": "Lección creada exitosamente", "id": nuevo_id}), 201