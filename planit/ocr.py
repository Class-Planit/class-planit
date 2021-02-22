

try:
    from PIL import Image
except ImportError:
    import Image
import pytesseract
from pytesseract import image_to_string
import PyPDF2
from PyPDF2 import PdfFileWriter, PdfFileReader
import requests
from PIL import Image, ImageFile, ImageDraw, ImageChops, ImageFilter, ImageEnhance

import fitz
from .models import *
import pdfplumber
from io import BytesIO
from urllib.request import FancyURLopener
from urllib.request import urlopen, Request
from django.core.files import File
from django.core.files.images import ImageFile



def pdf_pull_images(file_id, lesson_id, text_id):
    print('STARTED ++++++++++++')
    update_text = lessonPDFText.objects.get(id=file_id)
    lesson_match = lessonObjective.objects.get(id=lesson_id)
    url = update_text.pdf_doc.url
    rq = requests.get(url)

    pdf_file =fitz.open(stream=BytesIO(rq.content), filetype="application/pdf")

    for page_index in range(len(pdf_file)):
    # get the page itself
        page = pdf_file[page_index]
        image_list = page.getImageList()
        # printing number of images found in this page

        for image_index, img in enumerate(page.getImageList(), start=1):

            # get the XREF of the image
            xref = img[0]
            # extract the image bytes
            base_image = pdf_file.extractImage(xref)
            image_bytes = base_image["image"]
            # get the image extension
            image_ext = base_image["ext"]
            # load it to PIL
            image = Image.open(BytesIO(image_bytes))
            # save it to local disk
            image.save(open(f"image{page_index+1}_{image_index}.{image_ext}", "wb")) 

            p_index = str(int(page_index)+1)
            image_title = "image%s_%s.%s" % (p_index, str(image_index), str(image_ext))
            update_image = lessonPDFImage.objects.create(matched_lesson = lesson_match)
            update_image.image_image = ImageFile(open(image_title, "rb"))
            update_image.save()
 



def pdf_core(file_id): 
    update_text = lessonImageUpload.objects.get(id=file_id)
    url = update_text.image_image.url
    rq = requests.get(url) 

    im = Image.open(BytesIO(rq.content)) # the second one 
    im = im.filter(ImageFilter.MedianFilter())
    enhancer = ImageEnhance.Contrast(im)
    im = enhancer.enhance(2)
    im = im.convert('1')
    im.save('temp2.jpg')
    text = pytesseract.image_to_string(Image.open('temp2.jpg'))

    return(text)

 
def pdf_pull_text(file_id): 

    update_text = lessonPDFText.objects.get(id=file_id)
    url = update_text.pdf_doc.url 
    rq = requests.get(url)
    
    try:
        pdf = pdfplumber.load(BytesIO(rq.content))
        first_page = pdf.pages[0]
        
    except:
        pass

    return(first_page.extract_text())