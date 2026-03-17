import pytesseract
import cv2
import numpy as np
import sys
import os

# Configuración de ruta
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extraer_datos_placa(ruta_imagen):
    if not os.path.exists(ruta_imagen):
        return "Error: Imagen no encontrada"

    try:
        # 1. Leer imagen
        img = cv2.imread(ruta_imagen)
        
        # 2. Pre-procesamiento (Opcional pero recomendado para placas)
        # Convertimos a gris para que Tesseract no se confunda con colores
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # 3. OCR con tu modelo especializado
        # Usamos psm 6 porque las placas son bloques de texto
        texto = pytesseract.image_to_string(gray, lang="pam2", config='--psm 6')
        
        return texto.strip()
    except Exception as e:
        return f"Error procesando: {str(e)}"

if __name__ == "__main__":
    # Esto permite que lo llames desde la consola o desde Node.js
    if len(sys.argv) > 1:
        path = sys.argv[1]
        resultado = extraer_datos_placa(path)
        print(resultado)