import os
import base64
import requests

# 1. CONFIGURACIÓN
# Asegúrate de que la imagen esté en la misma carpeta o pon la ruta completa
RUTA_IMAGEN = "Mi1.jpeg" 
# Aquí puedes pegar tu llave directamente para la prueba rápida
API_KEY = "xd" 

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def probar_vision():
    if not os.path.exists(RUTA_IMAGEN):
        print(f"❌ No se encontró la imagen en: {RUTA_IMAGEN}")
        return

    base64_image = encode_image(RUTA_IMAGEN)

    # Estructura exacta que pide la API de Groq
    payload = {
        "model": "meta-llama/llama-4-scout-17b-16e-instruct",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Identifica este dispositivo de refrigeración. Dime la marca, el modelo y cualquier detalle técnico o especificación que logres leer en las etiquetas o el diseño."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        "temperature": 0.1
    }

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    print("⏳ Enviando imagen a Llama 4 Scout...")
    
    response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload)

    if response.status_code == 200:
        resultado = response.json()
        print("\n--- ANÁLISIS DEL MODELO ---")
        print(resultado['choices'][0]['message']['content'])
        print("---------------------------\n")
    else:
        print(f"❌ Error {response.status_code}: {response.text}")

if __name__ == "__main__":
    probar_vision()