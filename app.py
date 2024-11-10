from flask import Flask, request, jsonify
import os
import json
from google.oauth2 import service_account
from google.cloud import vision
import requests

app = Flask(__name__)

# Cargar credenciales desde la variable de entorno
credenciales_json = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")

# Verificar si se tienen credenciales y cargarlas
if credenciales_json:
    try:
        credentials_dict = json.loads(credenciales_json)
        credentials_info = service_account.Credentials.from_service_account_info(credentials_dict)
    except json.JSONDecodeError:
        raise ValueError("Las credenciales JSON proporcionadas no son válidas.")
else:
    raise ValueError("No se han proporcionado credenciales JSON válidas.")

# Crear cliente de Google Vision
client = vision.ImageAnnotatorClient(credentials=credentials_info)

@app.route('/analizar', methods=['POST'])
def analizar():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files['file']
    content = file.read()

    image = vision.Image(content=content)

    # Detectar etiquetas
    response = client.label_detection(image=image)
    etiquetas = response.label_annotations

    # Detectar texto en la imagen
    response_text = client.text_detection(image=image)
    texto = response_text.text_annotations

    # Generar consulta para búsqueda
    if texto:
        consulta = texto[0].description.strip().replace('\n', ' ')
    else:
        etiquetas_filtradas = [etiqueta.description for etiqueta in etiquetas if etiqueta.score > 0.8 and etiqueta.description.lower() not in ["liquid", "font", "rectangle", "material property", "tints and shades"]]
        consulta = ' '.join(etiquetas_filtradas)

    # URL de búsqueda de productos
    url = f"https://cosmosave.com/search?q={consulta}"
    return jsonify({"consulta": consulta, "resultado": url})

if __name__ == '__main__':
    app.run(debug=True)


