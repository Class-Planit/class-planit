from django.test import TestCase

# Create your tests here.
    def get(self, request, *args, **kwargs): 
        doc = fitz.open("planit/pdf_files/01_Identifying.pdf")
        pdfFileObj = open("planit/pdf_files/01_Identifying.pdf", 'rb')  
        # creating a pdf reader object  
        pdfReader = PyPDF2.PdfFileReader(pdfFileObj)  
        
        # creating a page object  
        pageObj = pdfReader.getPage(0)  
            
        # extracting text from page  
        results = pageObj.extractText()
        print(results)
        # closing the pdf file object  
       
    
        for i in range(len(doc)):
            for img in doc.getPageImageList(i):
                
                xref = img[0]
                pix = fitz.Pixmap(doc, xref)
                if pix.n < 5:       # this is GRAY or RGB
                    pix.writePNG("planit/pdf_files/p%s-%s.png" % (i, xref))
                  
                else:               # CMYK: convert to RGB first
                    pix1 = fitz.Pixmap(fitz.csRGB, pix)
                    pix1.writePNG("p%s-%s.png" % (i, xref))
                    pix1 = None
                pix = None
        return render(request, 'index.html', {})

    