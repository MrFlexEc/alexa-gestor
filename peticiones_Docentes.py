from flask import Blueprint,Flask, request, jsonify, render_template
from conexion import *
from flask_login import login_required

import uuid



docentes_ruta = Blueprint('docentes', __name__)

# Ruta principal que renderiza un archivo HTML
@docentes_ruta.route('/docentes/')
def home():
    return render_template('docentes.html')

# Ruta para manejar solicitudes GET a /api/data
@docentes_ruta.route('/obtener_docentes', methods=['GET'])
def get_docentes():
    client = connect_to_mongodb()
    try:
        db = client.AlexaGestor
        collection = db.docentes
        docentes = list(collection.find({}, {"_id": 1, "nombre_docente": 1, "apellido_docente": 1}))
        return jsonify(docentes), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        client.close()

# Ruta para manejar solicitudes PUT a /api/data
@docentes_ruta.route('/agregar/docente', methods=['PUT'])
def add_docente():
    data = request.get_json()
    print("Datos recibidos:", data)
    nombre_docente = data.get("nombre_docente")
    apellido_docente = data.get("apellido_docente")
    
    if not nombre_docente or not apellido_docente:
        print("Error: Faltan datos en la solicitud")
        return jsonify({"error": "Faltan datos"}), 400

    client = connect_to_mongodb()

    try:
        if client:
            print("Conexión exitosa a MongoDB")
            db = client.AlexaGestor
            collection = db.docentes
            
            # Generar un ID único
            docente_id = str(uuid.uuid4())

            docentes = {
                "_id": docente_id,
                "nombre_docente": nombre_docente,
                "apellido_docente": apellido_docente
            }
            result = collection.insert_one(docentes)
            print(f"Carrera {nombre_docente} añadida con ID: {docente_id}")
            client.close()
            return jsonify({"mensaje": f"Docente {nombre_docente} añadida con éxito", "id": docente_id}), 200
        else:
            print("Error: No se pudo conectar a MongoDB Atlas")
            return jsonify({"error": "No se pudo conectar a MongoDB Atlas"}), 500
    except Exception as e:
        print("Error:", e)
        return jsonify({"error": str(e)}), 500
    
@docentes_ruta.route('/eliminar/docente/<_id>', methods=['DELETE'])
def delete_docente(_id):
    client = connect_to_mongodb()
    try:
        db = client.AlexaGestor
        collection = db.docentes
        result = collection.delete_one({"_id": _id})
        if result.deleted_count == 1:
            return jsonify({"mensaje": f"Docente con id: {_id} eliminado con éxito"}), 200
        else:
            return jsonify({"error": f"No se encontró el docente con id: {_id}"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        client.close()

@docentes_ruta.route('/api/docentes', methods=['GET'])
def obtener_docentes():
    try:
        client = connect_to_mongodb()
        db = client.AlexaGestor
        collection = db.docentes

        # Excluir el campo "_id" de los resultados
        resultados = collection.find({})

        # Convertir los resultados a una lista de diccionarios
        docentes = [docente for docente in resultados]

        # Cerrar la conexión con MongoDB
        client.close()

        # Devolver los resultados como JSON
        return jsonify({"docentes": docentes}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Manejo de errores 404 (No encontrado)
@docentes_ruta.errorhandler(404)
def not_found(error):
    return jsonify({"error": "No encontrado"}), 404

# Manejo de errores 500 (Error interno del servidor)
@docentes_ruta.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Error interno del servidor"}), 500

# Si el script se ejecuta directamente, inicia el servidor de desarrollo de Flask