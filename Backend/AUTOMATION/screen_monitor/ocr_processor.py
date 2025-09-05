import cv2
import pytesseract
from pytesseract import Output

class OCRProcessor:
    """
    Wraps Tesseract OCR to emit bounding boxes of text above a
    confidence threshold.
    """

    def __init__(self, confidence: float = 60):
        self.conf = confidence
        # Adjust path below if Tesseract sits elsewhere
        pytesseract.pytesseract.tesseract_cmd = (
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"
        )

    def ocr_image(self, img):
        gray  = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        data  = pytesseract.image_to_data(gray, output_type=Output.DICT)
        boxes = []
        n     = len(data['text'])

        for i in range(n):
            txt  = data['text'][i].strip()
            conf = float(data['conf'][i] or -1)
            if txt and conf >= self.conf:
                boxes.append({
                    'text':  txt,
                    'left':  data['left'][i],
                    'top':   data['top'][i],
                    'width': data['width'][i],
                    'height':data['height'][i],
                    'conf':  conf
                })

        return boxes