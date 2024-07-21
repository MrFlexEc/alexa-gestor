from flask import Blueprint, request, jsonify, render_template, session

from conexion import connect_to_mongodb
import uuid

carreras_ruta = Blueprint('carreras', __name__)

# Función para verificar si el usuario está autenticado
def verificar_autenticacion():
    # Verificar si 'usuario_id' está en la sesión
    if 'usuario_id' not in session:
        # Redireccionar a la página de login si no está autenticado
        return False
    return True
# Ruta principal que renderiza un archivo HTML
@carreras_ruta.route('/carreras/')
def home():
    if not verificar_autenticacion():
            return render_template('Login.html')  # Redirecciona al login si no está autenticado
    return render_template('Carreras.html')
# Ruta para manejar solicitudes GET a /api/data
@carreras_ruta.route('/obtener_carreras', methods=['GET'])
def get_carreras():
    client = connect_to_mongodb()
    try:
        db = client.AlexaGestor
        collection = db.carreras
        carreras = list(collection.find({}, {"_id": 1, "nombre_carrera": 1}))
        return jsonify(carreras), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        client.close()

# Ruta para manejar solicitudes PUT a /api/data
@carreras_ruta.route('/agregar/carrera', methods=['PUT'])
def add_carrera():
    data = request.get_json()
    print("Datos recibidos:", data)
    nombre_carrera = data.get("nombre_carrera")
    descripcion = data.get("descripcion")
    
    if not nombre_carrera or not descripcion:
        print("Error: Faltan datos en la solicitud")
        return jsonify({"error": "Faltan datos"}), 400

    client = connect_to_mongodb()

    try:
        if client:
            print("Conexión exitosa a MongoDB")
            db = client.AlexaGestor
            collection = db.carreras
            
            # Generar un ID único
            carrera_id = str(uuid.uuid4())

            carrera = {
                "_id": carrera_id,
                "nombre_carrera": nombre_carrera,
                "descripcion": descripcion
            }
            result = collection.insert_one(carrera)
            print(f"Carrera {nombre_carrera} añadida con ID: {carrera_id}")
            client.close()
            return jsonify({"mensaje": f"Carrera {nombre_carrera} añadida con éxito", "id": carrera_id}), 200
        else:
            print("Error: No se pudo conectar a MongoDB Atlas")
            return jsonify({"error": "No se pudo conectar a MongoDB Atlas"}), 500
    except Exception as e:
        print("Error:", e)
        return jsonify({"error": str(e)}), 500

@carreras_ruta.route('/eliminar/carrera/<_id>', methods=['DELETE'])
def delete_carrera(_id):
    client = connect_to_mongodb()
    try:
        db = client.AlexaGestor
        collection = db.carreras
        result = collection.delete_one({"_id": _id})
        if result.deleted_count == 1:
            return jsonify({"mensaje": f"Carrera con id: {_id} eliminado con éxito"}), 200
        else:
            return jsonify({"error": f"No se encontró la carrera con id: {_id}"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        client.close()

@carreras_ruta.route('/api/carreras', methods=['GET'])
def obtener_carreras():
    try:
        client = connect_to_mongodb()
        db = client.AlexaGestor
        collection = db.carreras

        # Excluir el campo "_id" de los resultados
        resultados = collection.find({})

        # Convertir los resultados a una lista de diccionarios
        carreras = [carrera for carrera in resultados]

        # Cerrar la conexión con MongoDB
        client.close()

        # Devolver los resultados como JSON
        return jsonify({"carreras": carreras}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Manejo de errores 404 (No encontrado)
@carreras_ruta.errorhandler(404)
def not_found(error):
    return jsonify({"error": "No encontrado"}), 404

# Manejo de errores 500 (Error interno del servidor)
@carreras_ruta.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Error interno del servidor"}), 500
