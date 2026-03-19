import pytesseract
import cv2
import os
from jiwer import cer

# Configuración de Tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def cargar_ground_truth(ruta_txt):
    """Lee el archivo .txt de referencia."""
    with open(ruta_txt, 'r', encoding='utf-8') as f:
        texto = f.read().strip()
    return " ".join(texto.split())

def motor_base(img):
    """OCR Estándar."""
    # Usamos lang="eng" para el tesseract base
    texto = pytesseract.image_to_string(img, lang="eng")
    return " ".join(texto.strip().split())

def motor_pam2(img):
    """Tu modelo entrenado."""
    texto = pytesseract.image_to_string(lang="pam2")
    return " ".join(texto.strip().split())

def procesar_duelo(id_placa):
    # Ajustamos la ruta a tu estructura exacta
    base_path = "./imagenes/Nameplates/"
    
    # IMPORTANTE: Cambié .png por .jpg que es lo que me pasaste
    ruta_img = os.path.join(base_path, f"{id_placa}.jpg") 
    ruta_txt = os.path.join(base_path, f"{id_placa}.txt")

    if not os.path.exists(ruta_img) or not os.path.exists(ruta_txt):
        print(f"⚠️ Saltando {id_placa}:")
        print(f"   Buscando imagen en: {os.path.abspath(ruta_img)}")
        print(f"   Buscando texto en:  {os.path.abspath(ruta_txt)}")
        return

    img = cv2.imread(ruta_img)
    gt = cargar_ground_truth(ruta_txt)

    res_base = motor_base(img)
    res_pam2 = motor_pam2(img)

    err_base = cer(gt, res_base)
    err_pam2 = cer(gt, res_pam2)
    
    print(f"\n--- REPORTE DE PLACA: {id_placa} ---")
    print(f"{'MOTOR':<25} | {'ERROR (CER)':<12} | {'PRECISIÓN':<10}")
    print("-" * 55)
    print(f"{'Tesseract Base':<25} | {err_base*100:>10.2f}% | {100-(err_base*100):>9.2f}%")
    print(f"{'PAM2 Especializado':<25} | {err_pam2*100:>10.2f}% | {100-(err_pam2*100):>9.2f}%")
    
    if err_base > 0:
        mejora = ((err_base - err_pam2) / err_base * 100)
        print(f"🚀 MEJORA NETA: {mejora:.1f}%")

if __name__ == "__main__":
    # Si tus archivos se llaman E1.jpg y E1.txt, esto debería funcionar
    placas_a_testear = ["E1", "E2"]
    
    print("Iniciando Validación Cruzada de Modelos...")
    for placa in placas_a_testear:
        procesar_duelo(placa)