import pytesseract
import cv2

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

img = cv2.imread("./imagenes/Mias/Mi2.jpeg")
text = pytesseract.image_to_string(img, lang="pam2") 
print(text)