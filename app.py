from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from google.oauth2 import service_account
from google.cloud import vision

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Cargar credenciales desde la variable de entorno
credenciales_json = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")
print("Credenciales cargadas:", credenciales_json)  # Línea de depuración
if credenciales_json is None:
    raise ValueError("Las credenciales no están definidas en la variable de entorno 'GOOGLE_APPLICATION_CREDENTIALS_JSON'.")
credentials_info = service_account.Credentials.from_service_account_info(eval(credenciales_json))

# Crear cliente de Google Vision
client = vision.ImageAnnotatorClient(credentials=credentials_info)

@app.route('/', methods=['GET'])
def home():
    return "Bienvenido a la API de análisis de imágenes. Usa la ruta /analizar para subir una imagen.", 200

@app.route('/analizar', methods=['POST'])
def analizar():
    try:
        # Comprobación simple para verificar si la solicitud llega
        if 'file' not in request.files:
            return jsonify({"error": "No se proporcionó ningún archivo"}), 400

        file = request.files['file']
        content = file.read()

        if not content:
            return jsonify({"error": "El archivo está vacío"}), 400

        image = vision.Image(content=content)

        # Detectar etiquetas
        response = client.label_detection(image=image)
        if response.error.message:
            return jsonify({"error": f"Error de Google Vision: {response.error.message}"}), 500

        etiquetas = response.label_annotations

        # Detectar texto en la imagen
        response_text = client.text_detection(image=image)
        if response_text.error.message:
            return jsonify({"error": f"Error de Google Vision: {response_text.error.message}"}), 500

        texto = response_text.text_annotations

        # Generar consulta para búsqueda
        if texto:
            consulta = texto[0].description.strip().replace('\n', ' ')
        else:
            etiquetas_filtradas = [etiqueta.description for etiqueta in etiquetas if etiqueta.score > 0.8 and etiqueta.description.lower() not in ["liquid", "font", "rectangle", "material property", "tints and shades"]]
            consulta = ' '.join(etiquetas_filtradas)

        if not consulta:
            return jsonify({"error": "No se pudo generar una consulta a partir de la imagen proporcionada."}), 400

        # URL de búsqueda de productos
        url = f"https://cosmosave.com/search?q={consulta}"
        return jsonify({"consulta": consulta, "resultado": url})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)