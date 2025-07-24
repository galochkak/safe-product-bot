# utils/ocr.py
import pytesseract
from PIL import Image

def extract_text_from_image(file_name):
    try:
        image = Image.open(file_name)
        text = pytesseract.image_to_string(image, lang='rus+eng')
        return text.strip()
    except Exception as e:
        print(f"[Ошибка] Не удалось распознать текст: {e}")
        return ""