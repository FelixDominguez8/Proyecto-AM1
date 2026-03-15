import pytesseract
import cv2

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

img = cv2.imread("./imagenes/Nameplates/E2.jpg")
text = pytesseract.image_to_string(img, lang='pam2') #Con lang se especifica el idioma, si no se pone se deja en ingles por default
print(text)