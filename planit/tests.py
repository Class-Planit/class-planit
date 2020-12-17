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


        result_text = ' '.join(summary_list)
        keyword_results = get_keywords(result_text)


        topic_keywords = []        
        for item in keyword_results:
                 
                keyword_results_num = check_topic_relevance(item, lesson_id)
                if keyword_results_num >= .20:
                        
                        try:
                                wiki_search = wikipedia.search(item)
                                
                                
                                for item in wiki_search:
                                        try:
                                                topic_result = wikipedia.summary(item, sentences = 3, auto_suggest=False, redirect=True)
                                                
                                                result = check_topic_relevance(topic_result, lesson_id)
                                        
                                                if result >= .15:
                                                        new_result = result * 100 
                                                        
                                                        new_wiki, created = wikiTopic.objects.get_or_create(lesson_plan=class_objectives , topic=topic_result, relevance=new_result)
                                                
                                                        keyword_results_two = get_keywords(topic_result)
                                                        
                                                        for item in keyword_results_two:
                                                                if item not in topic_keywords:
                                                                        topic_keywords.append(item) 
                                                                        
                                                                        
                                        except wikipedia.DisambiguationError as e:
                                                pass

                        
                        except:
                                pass
        
        for item in topic_keywords:
                
                definitions = get_vocab_context(item)       
                if definitions:
                        keyword_result = check_topic_relevance(definitions , lesson_id)  
                        if keyword_result >= .30:
                                print(definitions, keyword_result)   