from google.oauth2 import service_account
from google.cloud import vision
import requests
from flask import Flask, request, jsonify
import os

# Inicializar la aplicación Flask
app = Flask(__name__)

# Cargar las credenciales desde el archivo JSON
# Cambio temporal para forzar el commit
credentials = service_account.Credentials.from_service_account_file('credenciales.json')

# Crear un cliente para la API de Google Vision
client = vision.ImageAnnotatorClient(credentials=credentials)

# Ruta principal para analizar imágenes
@app.route('/analizar', methods=['POST'])
def analizar_imagen():
    # Verificar si se ha enviado una imagen
    if 'imagen' not in request.files:
        return jsonify({'error': 'No se ha proporcionado ninguna imagen'}), 400

    imagen = request.files['imagen']
    content = imagen.read()

    # Procesar la imagen con Google Vision
    image = vision.Image(content=content)
    
    # Detectar etiquetas
    response = client.label_detection(image=image)
    etiquetas = response.label_annotations

    # Detectar texto en la imagen
    response_text = client.text_detection(image=image)
    texto = response_text.text_annotations

    # Si se encuentra texto, usarlo para la búsqueda
    if texto:
        consulta = texto[0].description.strip().replace('\n', ' ')
    else:
        # Si no hay texto, usar las etiquetas generales
        etiquetas_filtradas = [etiqueta.description for etiqueta in etiquetas if etiqueta.score > 0.8 and etiqueta.description.lower() not in ["liquid", "font", "rectangle", "material property", "tints and shades"]]
        consulta = ' '.join(etiquetas_filtradas)

    # Generar la URL de búsqueda en Shopify
    url_busqueda = f"https://cosmosave.com/search?q={consulta}"

    return jsonify({'consulta_generada': consulta, 'url_busqueda': url_busqueda})

# Ejecutar la aplicación en Heroku
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))


