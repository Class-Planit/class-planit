try:
    from PIL import Image
except ImportError:
    import Image
import pytesseract

import PyPDF2
from tika import parser





def pdf_core(filename):
    file_data = parser.from_file(filename)
    text = file_data['content']
    
    return(text)