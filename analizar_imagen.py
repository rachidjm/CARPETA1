from google.oauth2 import service_account
from google.cloud import vision
import requests

# Cargar las credenciales desde el archivo JSON que subiste en Shopify
credentials = service_account.Credentials.from_service_account_file('C:/Users/Rachi/Desktop/Carpeta1/Credenciales.json')

# Crear un cliente para la API de Google Vision
client = vision.ImageAnnotatorClient(credentials=credentials)

# Función para analizar la imagen subida por el usuario
def analizar_imagen(ruta_imagen):
    with open(ruta_imagen, 'rb') as image_file:
        content = image_file.read()

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
        # Filtrar etiquetas para eliminar las menos útiles
        etiquetas_filtradas = [etiqueta.description for etiqueta in etiquetas if etiqueta.score > 0.8 and etiqueta.description.lower() not in ["liquid", "font", "rectangle", "material property", "tints and shades"]]
        consulta = ' '.join(etiquetas_filtradas)

    print(f"Consulta Generada: {consulta}")

    # Llama a la función para buscar productos en Shopify con la consulta
    buscar_productos_shopify(consulta)

# Función para buscar en Shopify
def buscar_productos_shopify(consulta):
    # Configura la URL de búsqueda de Shopify
    url = f"https://cosmosave.com/search?q={consulta}"

    # Realiza la solicitud GET a la página de búsqueda de tu tienda
    respuesta = requests.get(url)

    # Imprime el enlace a los resultados de la búsqueda
    print(f"Resultados de la búsqueda: {respuesta.url}")

# Llama a la función con la imagen que sube el usuario
analizar_imagen('Prueba 1.jpg')

