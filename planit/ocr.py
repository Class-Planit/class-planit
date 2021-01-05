try:
    from PIL import Image
except ImportError:
    import Image
import pytesseract

import cv2
import PyPDF2
from tika import parser


def load_image(name):
    image = cv2.imread(name)
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)


def ocr_core(filename):
    # Include tesseract executable in your path

        books = load_image(filename)
     
        return(pytesseract.image_to_string(books))


def pdf_core(filename):
    file_data = parser.from_file(filename)
    text = file_data['content']
    
    return(text)