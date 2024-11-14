from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from google.oauth2 import service_account
from google.cloud import vision
from google.cloud.vision_v1 import types

app = Flask(__name__)
CORS(app)  # Habilitar CORS para todas las rutas

# Cargar credenciales desde el archivo JSON
try:
    credentials_info = service_account.Credentials.from_service_account_file("letus.json")
    print(f"Credenciales cargadas: {credentials_info}")
except Exception as e:
    print(f"Error al cargar credenciales: {e}")
    raise e

# Crear cliente de Google Vision
client = vision.ImageAnnotatorClient(credentials=credentials_info)

@app.route('/', methods=['GET'])
def home():
    return "Bienvenido a la API de análisis de imágenes. Usa la ruta /analizar para subir una imagen.", 200

@app.route('/analizar', methods=['POST'])
@app.route('/analizar/', methods=['POST'])
def analizar():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No se proporcionó ningún archivo"}), 400

        file = request.files['file']
        content = file.read()

        if not content:
            return jsonify({"error": "El archivo está vacío"}), 400

        image = types.Image(content=content)

        # Detectar texto en la imagen
        response_text = client.text_detection(image=image)
        if response_text.error.message:
            return jsonify({"error": f"Error de Google Vision (texto): {response_text.error.message}"}), 500

        texto = response_text.text_annotations

        if texto:
            consulta = ' '.join([t.description.replace('\n', ' ').strip() for t in texto if len(t.description) > 2])
        else:
            response = client.label_detection(image=image)
            etiquetas = response.label_annotations
            etiquetas_filtradas = [
                etiqueta.description for etiqueta in etiquetas
                if etiqueta.score > 0.9 and etiqueta.description.lower() not in [
                    "liquid", "font", "rectangle", "material property", "tints and shades", "packaging", "bottle"
                ]
            ]
            consulta = ' '.join(etiquetas_filtradas)

        if not consulta:
            return jsonify({"error": "No se pudo generar una consulta a partir de la imagen proporcionada."}), 400

        url = f"https://cosmosave.com/search?q={consulta}"
        return jsonify({"consulta": consulta, "resultado": url})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/test', methods=['GET'])
def test():
    return jsonify({"status": "La API está funcionando correctamente"}), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=True)
