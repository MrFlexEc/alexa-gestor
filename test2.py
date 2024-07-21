from conexion import *
def obtener_correos():
    client = connect_to_mongodb()
    if client:
        db = client.AlexaGestor
        collection = db.usuarios
        resultados = collection.find({}, {"correo": 1})
        
        correos = [resultado["correo"] for resultado in resultados]
        
        # Cerrar la conexión con MongoDB
        client.close()
        
        return correos
    else:
        return []
x= obtener_correos()
print(x)