from flask import Blueprint, request, jsonify, render_template, session, redirect, url_for
from conexion import connect_to_mongodb
import uuid

login_ruta = Blueprint('login', __name__)

# Ruta principal que renderiza un archivo HTML de login
@login_ruta.route('/')
def home():
    return render_template('Login.html')

# Ruta para verificar las credenciales y autenticar al usuario
@login_ruta.route('/sesion', methods=['POST'])
def verificarsesion():
    data = request.get_json()
    correo = data.get("correo")
    contrasenia = data.get("contrasenia")
    
    if not correo or not contrasenia:
        return jsonify({"error": "Faltan datos"}), 400

    client = connect_to_mongodb()

    try:
        db = client.AlexaGestor
        collection = db.usuarios
        usuario = collection.find_one({"correo": correo})
        
        if usuario and usuario["contrasenia"] == contrasenia:
            # Guardar el ID del usuario en la sesión
            session['usuario_id'] = str(usuario["_id"])
            session['usuario_nombre'] = usuario.get("nombres")  # Opcional: Guardar nombre en la sesión
            return jsonify({"mensaje": "Usuario autenticado con éxito"}), 200
        else:
            return jsonify({"error": "Credenciales incorrectas"}), 401
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        client.close()
# Ruta para cerrar sesión
@login_ruta.route('/logout', methods=['GET'])
def logout():
    # Eliminar todos los datos de la sesión
    session.clear()
    
    # Redirigir al usuario al login con un mensaje
    return redirect(url_for('login.home'))
