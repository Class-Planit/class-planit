try:
    from PIL import Image
except ImportError:
    import Image
import pytesseract

import PyPDF2
from tika import parser





def pdf_core(filename):
    file_data = parser.from_file(filename)
    # Create an image object of PIL library
    image = Image.open('F:/imagess.jpg')
    
    # pass image into pytesseract module
    # pytesseract is trained in many languages
    image_to_text = pytesseract.image_to_string(image, lang='eng')
    
    return(text)