import cv2
import numpy as np
import os

contador = 181

def procesar_etiqueta(ruta_imagen):
    global contador
    
    img = cv2.imread(ruta_imagen)
    if img is None:
        return

    # 1. IMAGEN DE ALTA CALIDAD (Versión de Limpieza Profunda para E7/E8 con ruido)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # --- PASO A: Reescalado Cúbico ---
    gray_high = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

    # --- PASO B: Desenfoque Mediano (Anti-puntos) ---
    # El filtro mediano es brutal con los puntitos negros tipo "sal y pimienta".
    # El '5' es el tamaño del filtro, debe ser impar. Prueba con 3 o 5.
    gray_clean = cv2.medianBlur(gray_high, 5)
    
    # --- PASO C: Binarización Adaptativa ---
    # Usamos Gaussian C para un resultado más suave.
    # El '21' es el tamaño del bloque, súbelo si las letras son grandes.
    # El '10' es la constante que resta, súbela para limpiar más el fondo.
    binary_high = cv2.adaptiveThreshold(gray_clean, 255, 
                                        cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                        cv2.THRESH_BINARY, 21, 10)

    # --- PASO D: Operación Morfológica (Apertura) ---
    # Esto elimina objetos negros que sean más pequeños que el núcleo definido.
    # Crear un núcleo (kernel) de 2x2 o 3x3 para erosionar el ruido.
    kernel = np.ones((2,2), np.uint8)
    binary_high = cv2.morphologyEx(binary_high, cv2.MORPH_OPEN, kernel)

    # Si la imagen sale invertida (letras blancas), descomenta la línea de abajo:
    # binary_high = cv2.bitwise_not(binary_high)

    # 2. IMAGEN DE VISTA (Lo que tú ves para recortar)
    monitor_h = 750 # Ajustado para que quepa en cualquier pantalla
    escala_vista = monitor_h / binary_high.shape[0]
    vista_previa = cv2.resize(binary_high, None, fx=escala_vista, fy=escala_vista)

    # --- EL TRUCO DEL CONTRASTE ---
    # Convertimos el blanco en gris oscuro para que el cuadro blanco de OpenCV RESALTE
    # Blanco (255) -> Gris (60) | Negro (0) -> Negro (0)
    vista_contraste = np.where(vista_previa == 255, 60, 0).astype(np.uint8)
    # ------------------------------

    while True:
        titulo = f"LINEA {contador:03d} | ENTER=Guardar | ESC=Salir de esta foto"
        
        # Ahora el cuadro blanco de selectROI será CLARAMENTE visible sobre el fondo gris
        r = cv2.selectROI(titulo, vista_contraste, fromCenter=False, showCrosshair=True)
        
        if r[2] == 0 or r[3] == 0:
            break
            
        # Mapeo a la imagen de ALTA CALIDAD
        x, y, w, h = [int(v / escala_vista) for v in r]
        recorte_final = binary_high[y:y+h, x:x+w]
        
        # Guardado en TIFF sin pérdida
        os.makedirs("./imagenes/Salida/", exist_ok=True)
        nombre_base = f"linea_{contador:03d}"
        cv2.imwrite(f"./imagenes/Salida/{nombre_base}.tiff", recorte_final, [cv2.IMWRITE_TIFF_COMPRESSION, 1])
        
        # Generar el archivo .gt.txt vacío
        with open(f"./imagenes/Salida/{nombre_base}.gt.txt", "w", encoding="utf-8") as f:
            f.write("")
            
        print(f"OK -> {nombre_base}.tiff")
        contador += 1

    cv2.destroyAllWindows()

procesar_etiqueta('./imagenes/Nameplates/E8.jpg')