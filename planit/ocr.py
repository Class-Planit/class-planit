

try:
    from PIL import Image
except ImportError:
    import Image
import os
import pytesseract
from pytesseract import image_to_string
import PyPDF2
from PyPDF2 import PdfFileWriter, PdfFileReader
import requests
from PIL import Image, ImageFile, ImageDraw, ImageChops, ImageFilter, ImageEnhance
pytesseract.pytesseract.tesseract_cmd = '/app/.apt/usr/bin/tesseract'
import fitz
from .models import *
import pdfplumber
from io import BytesIO, StringIO
from urllib.request import FancyURLopener
from urllib.request import urlopen, Request
from django.core.files import File
from django.core.files.images import ImageFile
from pprint import pprint
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser
from .textbook_matching import *

def get_question_text_ocr(textlines):
    text_list_join = ''.join([str(i) for i in textlines])
    results = tokenize.sent_tokenize(text_list_join)
    all_topic_lines = []
    for sent in results:
        sent = ' '.join(sent.split())
        questions = ['What ', 'Where ', 'How ', 'When ', 'Which ', 'Explain ', 'Discuss ', 'Describe ']
        for quest in questions:
            if quest in sent:
                all_topic_lines.append(sent)


    return(all_topic_lines)

def find_match_topic_texts(subject, text_id):
    #ensure the matching is subject specific 
    topics = topicInformation.objects.filter(subject = subject)
    titles = textBookTitle.objects.get(id=text_id)
    textlines = textBookBackground.objects.filter(textbook=titles)
    matched_topics = []
    for line in textlines:
        line_id = line.id
        text = line.line_text
        for topic in topics:
            topic_id = topic.id
            word = topic.item 
            if word.lower() in text.lower():
                update_topic = topicInformation.objects.get(id=topic_id)
                matched_topics.append(update_topic)

    return(matched_topics)

def match_topic_texts(subject, text_id):
    #ensure the matching is subject specific 
    topics = topicInformation.objects.filter(subject = subject)
    titles = textBookTitle.objects.get(id=text_id)
    textlines = textBookBackground.objects.filter(textbook=titles)
    for line in textlines:
        line_id = line.id
        text = line.line_text
        for topic in topics:
            topic_id = topic.id
            word = topic.item 
            if word.lower() in text.lower():
                update_topic = topicInformation.objects.get(id=topic_id)
                update_line = textBookBackground.objects.get(id=line_id)
                update_topic.text_index.add(line_id)




def get_pdf_sent(match_textlines):
    full_sent_list = []
    text_list_join = ''.join([str(i) for i in match_textlines])
    results = tokenize.sent_tokenize(text_list_join)

    for sent in results:
        sent = ' '.join(sent.split())
        is_verb = False
        is_noun = False
        is_long = False
        sent = sent.replace('|', ' ')
        sent_blob = TextBlob(sent)
        sent_tagger = sent_blob.pos_tags
        for y in sent_tagger:
            if len(y[1]) > 2:
                is_long = True
        for y in sent_tagger:
            if 'V' in y[1]:
                is_verb = True
        for y in sent_tagger:
            if 'NNP' in y[1]:
                is_noun = True
            elif 'NNPS' in y[1]:
                is_noun = True
        remove_list = ['illustrations', 'cartoon', 'Figure', 'they', 'those', 'Circle ', 'Education.com']
        results = []
        if is_verb and is_noun and is_long:
            sent = re.sub(r'\(.*\)', '', sent)
            sent = re.sub('Chapter', '', sent)
            sent = re.sub('Rule Britannia!', '', sent)
            sent = re.sub('Description', '', sent)
            if any(word in sent for word in remove_list):
                pass
            else:
                if sent not in full_sent_list:
                    full_sent_list.append(sent_tagger)
    
    return(full_sent_list)


def pdf_pull_images(file_id, lesson_id, text_id, week_of):
    textbook_match = textBookTitle.objects.get(id=text_id)
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
            image.save(open(f"image{page_index+1}_{image_index}_{week_of}.{image_ext}", "wb")) 

            p_index = str(int(page_index)+1)
            image_title = "image%s_%s_%s.%s" % (p_index, str(image_index), str(week_of), str(image_ext))
            update_image = lessonPDFImage.objects.create(matched_lesson = lesson_match)
            update_image.image_image = ImageFile(open(image_title, "rb"))
            update_image.page_counter = page_index
            update_image.textbook = textbook_match
            update_image.save()
            os.remove(image_title) 




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
    url_open = urlopen(Request(url)).read()
    
    # Cast to StringIO object

    memory_file = BytesIO(rq.content)

    output_string = StringIO()
    # Create a PDF parser object associated with the StringIO object
    parser = PDFParser(memory_file)

    doc = PDFDocument(parser)

    rsrcmgr = PDFResourceManager()
    device = TextConverter(rsrcmgr, output_string, laparams=LAParams())
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    page_index = 0
    for page in PDFPage.create_pages(doc):
        page_index = page_index + 1
    
        interpreter.process_page(page)
   
 

    return(output_string.getvalue())


def build_textbook(file_id, user_id, class_id, lesson_id, week_of):
    user_profile = User.objects.get(id=user_id)
    classroom_profile = classroom.objects.get(id=class_id)
    class_objectives = lessonObjective.objects.get(id=lesson_id)
    grade_levels = classroom_profile.grade_level.all()
    matched_grade_levels = gradeLevel.objects.filter(id__in=grade_levels)
    subject = class_objectives.subject
    standard_match = standardSet.objects.get(id=classroom_profile.standards_set_id)

    worksheet_title = '%s: %s for week of %s' % (user_profile, subject, week_of) 

    textbook_match, created = textBookTitle.objects.get_or_create(title=worksheet_title, standards_set=standard_match, subject=subject, uploaded_by=user_profile, lesson_id_num=lesson_id)
    for grade in grade_levels:
            update_text = textbook_match.grade_level.add(grade)
            
    text_id = textbook_match.id
    update_text = lessonPDFText.objects.get(id=file_id)
    url = update_text.pdf_doc.url 
    rq = requests.get(url)
    url_open = urlopen(Request(url)).read()
    
    # Cast to StringIO object

    memory_file = BytesIO(rq.content)

    # Create a PDF parser object associated with the StringIO object
    parser = PDFParser(memory_file)

    doc = PDFDocument(parser)

    page_index = 0
 
    for page in PDFPage.create_pages(doc):
        output_string = StringIO()
        rsrcmgr = PDFResourceManager()
        device = TextConverter(rsrcmgr, output_string, laparams=LAParams())
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        page_index = page_index + 1

        interpreter.process_page(page)

        content = output_string.getvalue()
        
        
        split_content = split_into_sentences(content)

        for line in split_content:
            get_lemma = stemSentence(line)
            obj, created = textBookBackground.objects.get_or_create(textbook=textbook_match, line_text=line, line_lemma=get_lemma)
            obj.line_counter = int(str(text_id) + str(obj.id)) 
            obj.page_counter = page_index
            obj.save()
            match_topic_texts(subject, text_id)

    pdf_pull_images(file_id, lesson_id, text_id, week_of)

    return('done')