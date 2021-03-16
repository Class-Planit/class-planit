from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View, FormView, TemplateView, DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic.edit import FormMixin
from django.template.loader import render_to_string
from django.urls import reverse_lazy
import _datetime
from datetime import datetime
from django.views.generic import TemplateView
from chartjs.views.lines import BaseLineChartView
from django.forms import modelformset_factory, inlineformset_factory
import random
try:
    from PIL import Image
except ImportError:
    import Image
import pytesseract
import csv, io
from django.template.loader import get_template
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from twilio.rest import Client
from twilio.rest import TwilioRestClient
from pytesseract import image_to_string
from .forms import *
from .models import *
from .match_standards import *
from .textbook_matching import *
from .word_cluster import *
from .topic_matching import *
from .ocr import *
from weasyprint import HTML, CSS
import tempfile
from .tasks import *
from .get_questions import *
from .lesson_planner import *
# Create your views here.
# Create your views here.











    


def SelectKeywords(request, user_id=None, class_id=None, subject=None, lesson_id=None):
    current_week = date.today().isocalendar()[1] 
    user_profile = User.objects.get(id=user_id)

    classroom_profile = classroom.objects.get(id=class_id)
    grade_list = classroom_profile.grade_level.all()

    standard_match = standardSet.objects.get(id=classroom_profile.standards_set_id)

    subjects_list = classroom_profile.subjects.all()
    subject_matches = standardSubjects.objects.filter(id__in=subjects_list)
    

    class_objectives = lessonObjective.objects.all().order_by('subject')
    vocab_list = vocabularyList.objects.filter(lesson_plan__in=class_objectives)
    lesson_activities = lessonFull.objects.filter(lesson_overview__in=class_objectives)
    lesson_match = lessonObjective.objects.get(id=lesson_id)
    lesson_standards = singleStandard.objects.filter(id__in=lesson_match.objectives_standards.all())
    teacher_objective = lesson_match.teacher_objective

    subject = lesson_match.subject
    related_question = googleRelatedQuestions.objects.filter(lesson_plan=lesson_match, is_selected=False)
    related_topics = googleSearchResult.objects.filter(lesson_plan=lesson_match, is_selected=False)

    questions_selected = googleRelatedQuestions.objects.filter(lesson_plan=lesson_match, is_selected=True)
    topics_selected = googleSearchResult.objects.filter(lesson_plan=lesson_match, is_selected=True)
    selected_wiki = wikiTopic.objects.filter(lesson_plan=lesson_match, is_selected=True)


    wiki_topics = wikiTopic.objects.filter(lesson_plan=lesson_match).exclude(is_selected=True).order_by('-relevance')
    matched_backgroud_topics = match_topics(teacher_objective, class_id, lesson_id)
    
    wiki_count = selected_wiki.count()
    google_count = topics_selected.count()
    total = wiki_count + google_count
    
    
    youtube_matches = youtube_results(teacher_objective, lesson_id)
    if youtube_matches:
        youtube_list = youtube_matches[:5]
    else:
        youtube_list = []

    vid_id_list = []
    for result in youtube_list:
        try: 
            link = result['link']
            vid_id = video_id(link)
            description = result['description']
            title = result['title']
            youtube_create, created = youtubeSearchResult.objects.get_or_create(lesson_plan=lesson_match, title=title, description=description, vid_id=vid_id)
            vid_id_list.append(youtube_create)
        except:
            pass

    step = 3
    return render(request, 'dashboard/create_objective.html', {'user_profile': user_profile, 'selected_wiki': selected_wiki, 'vid_id_list': vid_id_list, 'questions_selected': questions_selected, 'topics_selected': topics_selected,  'related_question': related_question, 'related_topics': related_topics, 'wiki_topics': wiki_topics, 'step': step, 'lesson_standards': lesson_standards, 'lesson_match': lesson_match, 'lesson_activities': lesson_activities, 'class_objectives': class_objectives, 'current_week': current_week, 'classroom_profile': classroom_profile})

def SelectTopic(request):
    if request.method == 'GET':
        topic_id = request.GET['topic_id']
        lesson_id = request.GET['lesson_id']
        lesson_match = lessonObjective.objects.get(id=lesson_id)
        topic_match = topicInformation.objects.get(id=topic_id)
        update_lesson = lesson_match.objectives_topics.add(topic_match)
        return HttpResponse("Topic Added!")
    else:
        return HttpResponse("Request method is not a GET")

def SelectRelatedInformation(request, user_id=None, class_id=None, subject=None, lesson_id=None, type_id=None, item_id=None, action=None):
    user_profile = User.objects.get(id=user_id)
    classroom_profile = classroom.objects.get(id=class_id)
    #Keyword = 1 , Google Topic = 2, Question = 3, Wiki Topic = 5  
    type_id = int(type_id)
    if type_id == 1: 
        keyword_match = keywordResults.objects.get(id=item_id)
        action = int(action)
        if action == 0:
            keyword_match.is_selected = True
            keyword_match.save()
        elif action == 2:
            keyword_match.delete()
        else:
            keyword_match.is_selected = False
            keyword_match.save()
        return redirect('{}#keywords'.format(reverse('select_keywords_two', kwargs={'user_id':user_profile.id, 'class_id':classroom_profile.id, 'subject':subject, 'lesson_id':lesson_id})))
    elif type_id == 2:
        keyword_match = googleSearchResult.objects.get(id=item_id)
        action = int(action)
        if action == 0:
            keyword_match.is_selected = True
            keyword_match.save()
        elif action == 2:
            keyword_match.delete()
        else:
            keyword_match.is_selected = False
            keyword_match.save()
        return redirect('{}#keywords'.format(reverse('select_keywords', kwargs={'user_id':user_profile.id, 'class_id':classroom_profile.id, 'subject':subject, 'lesson_id':lesson_id})))
    elif type_id == 3:
        keyword_match = googleRelatedQuestions.objects.get(id=item_id)
        action = int(action)
        if action == 0:
            keyword_match.is_selected = True
            keyword_match.save()
        elif action == 2:
            keyword_match.delete()
        else:
            keyword_match.is_selected = False
            keyword_match.save()
        return redirect('{}#keywords'.format(reverse('select_keywords', kwargs={'user_id':user_profile.id, 'class_id':classroom_profile.id, 'subject':subject, 'lesson_id':lesson_id})))
    elif type_id == 7:
        keyword_match = youtubeSearchResult.objects.get(id=item_id)
        action = int(action)
        if action == 0:
            keyword_match.is_selected = True
            keyword_match.save()
        else:
            keyword_match.is_selected = False
            keyword_match.save()
        return redirect('{}#youtube'.format(reverse('select_keywords', kwargs={'user_id':user_profile.id, 'class_id':classroom_profile.id, 'subject':subject, 'lesson_id':lesson_id})))
    elif type_id == 6:
        lesson_match = lessonObjective.objects.get(id=lesson_id)
        topic_match = topicInformation.objects.get(id=item_id)
        action = int(action)
        if action == 0:
            update_lesson = lesson_match.objectives_topics.remove(topic_match)
        else:
            update_lesson = lesson_match.objectives_topics.add(topic_match)
        return redirect('{}#keywords'.format(reverse('activity_builder', kwargs={'user_id':user_profile.id, 'class_id':classroom_profile.id, 'subject':subject, 'lesson_id':lesson_id})))
    elif type_id == 8:
        lesson_match = lessonObjective.objects.get(id=lesson_id)
        topic_match = topicInformation.objects.get(id=item_id)
        action = int(action)
        if action == 0:
            update_lesson = lesson_match.objectives_topics.remove(topic_match)
        else:
            update_lesson = lesson_match.objectives_topics.add(topic_match)
        return redirect('{}#youtube'.format(reverse('select_standards_two', kwargs={'user_id':user_profile.id, 'class_id':classroom_profile.id, 'subject':subject, 'lesson_id':lesson_id, 'select_all':False})))
    elif type_id == 10:
        lesson_match = lessonObjective.objects.get(id=lesson_id)
        topic_match = selectedActivity.objects.get(id=item_id)
        action = int(action)
        if action == 0:
            topic_match.is_selected = True 
            topic_match.save()
        else:
            topic_match.is_selected = False
            topic_match.save()
        return redirect('{}#keywords'.format(reverse('activity_builder', kwargs={'user_id':user_profile.id, 'class_id':classroom_profile.id, 'subject':subject, 'lesson_id':lesson_id})))
    else:
        keyword_match = wikiTopic.objects.get(id=item_id)
        action = int(action)
        if action == 0:
            keyword_match.is_selected = True
            keyword_match.save()
        elif action == 2:
            keyword_match.delete()
        else:
            keyword_match.is_selected = False
            keyword_match.save()
        return redirect('{}#keywords'.format(reverse('select_keywords', kwargs={'user_id':user_profile.id, 'class_id':classroom_profile.id, 'subject':subject, 'lesson_id':lesson_id})))




def ActivityBuilder(request, user_id=None, class_id=None, subject=None, lesson_id=None):
    current_week = date.today().isocalendar()[1] 
    user_profile = User.objects.get(id=user_id)

    classroom_profile = classroom.objects.get(id=class_id)
    grade_list = classroom_profile.grade_level.all()

    standard_match = standardSet.objects.get(id=classroom_profile.standards_set_id)

    subjects_list = classroom_profile.subjects.all()
    subject_matches = standardSubjects.objects.filter(id__in=subjects_list )                                         
    
    
    class_objectives = lessonObjective.objects.all().order_by('subject')
    vocab_list = vocabularyList.objects.filter(lesson_plan__in=class_objectives)
    lesson_activities = lessonFull.objects.filter(lesson_overview__in=class_objectives)
    lesson_match = lessonObjective.objects.get(id=lesson_id)
    question_match = match_lesson_questions(lesson_match.teacher_objective, class_id, lesson_id)
    lesson_standards = singleStandard.objects.filter(id__in=lesson_match.objectives_standards.all())
    topic_matches = lesson_match.objectives_topics.all()
    topic_lists_selected = topicInformation.objects.filter(id__in=topic_matches).order_by('item')
    topic_count = topic_lists_selected.count()
    chunks = topic_count/3
    one_end = chunks
    two_end = one_end + chunks 
    three_end = two_end + chunks 

    first_topics = topicInformation.objects.filter(id__in=topic_matches).order_by('item')[0:one_end]
    second_topics = topicInformation.objects.filter(id__in=topic_matches).order_by('item')[one_end:two_end]
    third_topics = topicInformation.objects.filter(id__in=topic_matches).order_by('item')[two_end:three_end]
    uploaded_images = lessonPDFImage.objects.filter(matched_lesson=lesson_match)
    uploaded_text = lessonPDFText.objects.filter(matched_lesson=lesson_match)


    text_questions = get_question_text(lesson_id)
    match_textlines = get_cluster_text(lesson_id,user_id)


    topic_results = []
    for item in topic_lists_selected:
        topic_results.append(item.id)

    topic_lists_matched = topicInformation.objects.filter(id__in=topic_results).order_by('item')

    if match_textlines: 
        summarize_text = summ_text(match_textlines)
        sent_text = get_statment_sent(match_textlines)
    else:
        summarize_text = []
        sent_text = []

    teacher_objective = lesson_match.teacher_objective
    
    lesson_results = []

    questions_selected = googleRelatedQuestions.objects.filter(lesson_plan=lesson_match, is_selected=True)
    topics_selected = googleSearchResult.objects.filter(lesson_plan=lesson_match, is_selected=True)

    keywords_selected = keywordResults.objects.filter(lesson_plan=lesson_match, is_selected=True).order_by('-relevance')
    keywords_matched = keywordResults.objects.filter(lesson_plan=lesson_match, is_selected=False).order_by('-relevance')
    matched_topics = match_topics(teacher_objective, class_id, lesson_id)
    
    text_update, created = lessonText.objects.get_or_create(matched_lesson=lesson_match)
    lessons_wording = text_update.activities
    lesson_activities_matched = get_lessons(lesson_id, user_id)
    
    selected_activities = selectedActivity.objects.filter(lesson_overview=lesson_match, is_selected=True)
    not_selected_activities = selectedActivity.objects.filter(lesson_overview=lesson_match, is_selected=False).order_by('bloom')

    if selected_activities:
        lesson_analytics = label_activities_analytics(lesson_id)
    else:
        lesson_analytics = []


    if text_update.activities:
        split_activities = split_matched_activities(text_update.activities, class_id, lesson_id, user_id)

    if text_update.overview:
        split_text = split_matched_text(text_update.overview) 
        split_terms = split_matched_terms(text_update.lesson_terms, class_id, lesson_id) 
        question_list = []
        for line_topic in topic_matches:
            for description_item in line_topic.description.all():
                sentence = line_topic.item + ' - ' + description_item.description
                results = genQuestion(sentence, line_topic.item)
                if results:
                    question_list.append(results)
                else:
                    pass
        text_match = match_lesson_topics(text_update.overview, class_id, lesson_id) 
        
    else:
        split_text = []
        text_match = [] 
        
        question_list = []
    
    
    question_lists = []
    if question_match:
        for item in question_match:
            result_id = item[0][0]

            topic = topicQuestion.objects.get(id=result_id)
    
            question_lists.append(topic )
    
    if question_match:
        pass
    else:
        question_match = []

    combined = matched_topics, text_match
    topic_lists = []
    if combined:
        for text_lists in combined:
            if text_lists:
                for item in text_lists:

                    topic = topicInformation.objects.get(id=item[0][0])

                    word_term = topic.item
                    word_split = word_term.split()
                    word_count = len(word_split)
                    if lesson_match.objectives_topics.filter(id=topic.id).exists():
                        pass
                    else:
                        result = topic, word_count 
                        if result in topic_lists:
                            pass
                        else:
                            topic_lists.append(result)

    topic_lists.sort(key=lambda x: x[1])

    if topic_lists_matched:
        generated_questions = []
        for item in topic_lists_matched:
            generated_quest = generate_questions_topic(item.id)
            if generated_quest:
                generated_questions.append(generated_quest[0])
    else:
        generated_questions = []

    youtube_matched = youtubeSearchResult.objects.filter(lesson_plan=lesson_match, is_selected=True)
    

    
    step = 4

    return render(request, 'dashboard/activity_builder.html', {'user_profile': user_profile, 'summarize_text': summarize_text, 'lesson_analytics': lesson_analytics, 'generated_questions': generated_questions, 'question_lists': question_lists,  'first_topics': first_topics, 'second_topics': second_topics, 'third_topics': third_topics, 'topic_lists_matched': topic_lists_matched, 'sent_text': sent_text,  'match_textlines': match_textlines, 'text_questions': text_questions, 'selected_activities': selected_activities, 'not_selected_activities':not_selected_activities, 'question_list': question_list, 'lessons_wording': lessons_wording, 'question_lists': question_lists, 'text_update': text_update, 'lesson_results': lesson_results, 'topic_lists_selected': topic_lists_selected, 'topic_lists': topic_lists, 'keywords_selected': keywords_selected, 'youtube_matched': youtube_matched, 'questions_selected': questions_selected, 'topics_selected': topics_selected, 'keywords_matched': keywords_matched, 'step': step, 'lesson_standards': lesson_standards, 'lesson_match': lesson_match, 'lesson_activities': lesson_activities, 'class_objectives': class_objectives, 'current_week': current_week, 'classroom_profile': classroom_profile})




def DigitalActivities(request, user_id=None, class_id=None, subject=None, lesson_id=None, act_id=None):
    current_week = date.today().isocalendar()[1] 
    user_profile = User.objects.get(id=user_id)

    classroom_profile = classroom.objects.get(id=class_id)
    grade_list = classroom_profile.grade_level.all()

    standard_match = standardSet.objects.get(id=classroom_profile.standards_set_id)


    worksheet_title = '%s: %s for week of %s' % (user_profile, classroom_profile, current_week) 
    class_objectives = lessonObjective.objects.all().order_by('subject')
    vocab_list = vocabularyList.objects.filter(lesson_plan__in=class_objectives)
    lesson_activities = lessonFull.objects.filter(lesson_overview__in=class_objectives)
    lesson_match = lessonObjective.objects.get(id=lesson_id)
    subject_match = lesson_match.subject_id
    subject_match_full = standardSubjects.objects.get(id=subject_match) 
    question_match = match_lesson_questions(lesson_match.teacher_objective, class_id, lesson_id)
    lesson_standards = singleStandard.objects.filter(id__in=lesson_match.objectives_standards.all())
    topic_matches = lesson_match.objectives_topics.all()
    topic_lists_selected = topicInformation.objects.filter(id__in=topic_matches).order_by('item')
    topic_count = topic_lists_selected.count()
    chunks = topic_count/3
    one_end = chunks
    two_end = one_end + chunks 
    three_end = two_end + chunks 

    if 'False' in act_id:
        pass
    else:
        act_id = int(act_id)
        get_worksheet, created = worksheetFull.objects.get_or_create(created_by=user_profile, title=worksheet_title)
        get_text = textBookBackground.objects.get(id=act_id)
        
        context = get_text.line_text
        get_question, created = topicQuestion.objects.get_or_create(linked_text=get_text, subject=subject_match_full, Question=context, standard_set= standard_match, created_by=user_profile)
        if get_worksheet.questions.filter(id=get_question.id).exists():
            pass
        else:
            update_worksheet = get_worksheet.questions.add(get_question)
    
    matched_worksheet = worksheetFull.objects.filter(created_by=user_profile, title=worksheet_title).first()
    text_results = []
    if matched_worksheet:
        all_question = matched_worksheet.questions.all()
        
        for quest in all_question:
            textbook = quest.linked_text_id
            text_results.append(textbook)


    matched_textbook_background = textBookBackground.objects.filter(id__in=text_results)
    uploaded_text_topics = match_topics_text_uploads(matched_textbook_background, class_id, lesson_id,)
    find_more_topics = find_match_topic_texts(subject_match_full.subject_title, text_id)


    first_topics = topicInformation.objects.filter(id__in=topic_matches).order_by('item')[0:one_end]
    second_topics = topicInformation.objects.filter(id__in=topic_matches).order_by('item')[one_end:two_end]
    third_topics = topicInformation.objects.filter(id__in=topic_matches).order_by('item')[two_end:three_end]
    uploaded_images = lessonPDFImage.objects.filter(matched_lesson=lesson_match)

    uploaded_text = lessonPDFText.objects.filter(matched_lesson=lesson_match)

    text_questions = get_question_text(lesson_id)
    match_textlines = get_cluster_text(lesson_id,user_id)
    print('1-------', match_textlines)

    topic_results = []
    for item in topic_lists_selected:

        topic_results.append(item.id)

    topic_lists_matched = topicInformation.objects.filter(id__in=topic_results).order_by('item')

    if match_textlines: 
        summarize_text = summ_text(match_textlines)
        sent_text = get_statment_sent(match_textlines)
    else:
        summarize_text = []
        sent_text = []

    teacher_objective = lesson_match.teacher_objective
    
    lesson_results = []

    questions_selected = googleRelatedQuestions.objects.filter(lesson_plan=lesson_match, is_selected=True)
    topics_selected = googleSearchResult.objects.filter(lesson_plan=lesson_match, is_selected=True)

    keywords_selected = keywordResults.objects.filter(lesson_plan=lesson_match, is_selected=True).order_by('-relevance')
    keywords_matched = keywordResults.objects.filter(lesson_plan=lesson_match, is_selected=False).order_by('-relevance')
    matched_topics = match_topics(teacher_objective, class_id, lesson_id)
    
    text_update, created = lessonText.objects.get_or_create(matched_lesson=lesson_match)
    lessons_wording = text_update.activities
    lesson_activities_matched = get_lessons(lesson_id, user_id)
    
    selected_activities = selectedActivity.objects.filter(lesson_overview=lesson_match, is_selected=True)
    not_selected_activities = selectedActivity.objects.filter(lesson_overview=lesson_match, is_selected=False).order_by('bloom')

    if selected_activities:
        lesson_analytics = label_activities_analytics(lesson_id)
    else:
        lesson_analytics = []


    if text_update.activities:
        split_activities = split_matched_activities(text_update.activities, class_id, lesson_id, user_id)

    if text_update.overview:
        split_text = split_matched_text(text_update.overview) 
        split_terms = split_matched_terms(text_update.lesson_terms, class_id, lesson_id) 
        question_list = []
        for line_topic in topic_matches:
            for description_item in line_topic.description.all():
                sentence = line_topic.item + ' - ' + description_item.description
                results = genQuestion(sentence, line_topic.item)
                if results:
                    question_list.append(results)
                else:
                    pass
        text_match = match_lesson_topics(text_update.overview, class_id, lesson_id) 
        
    else:
        split_text = []
        text_match = [] 
        
        question_list = []
    
    
    question_lists = []
    if question_match:
        for item in question_match:
            result_id = item[0][0]

            topic = topicQuestion.objects.get(id=result_id)
    
            question_lists.append(topic )
    
    if question_match:
        pass
    else:
        question_match = []


    combined = uploaded_text_topics + text_match + matched_topics 

    topic_lists = []
    if combined:
        for text_lists in combined:

            topic_id = text_lists[0][0]

            topic = topicInformation.objects.get(id=topic_id)

            word_term = topic.item
            word_split = word_term.split()
            word_count = len(word_split)
            if lesson_match.objectives_topics.filter(id=topic.id).exists():
                pass
            else:
                result = topic, word_count 
                if result in topic_lists:
                    pass
                else:
                    topic_lists.append(result)

    topic_lists.sort(key=lambda x: x[1])

    if topic_lists_matched:
        generated_questions = []
        for item in topic_lists_matched:
            generated_quest = generate_questions_topic(item.id)
            if generated_quest:
                generated_questions.append(generated_quest[0])
    else:
        generated_questions = []

    youtube_matched = youtubeSearchResult.objects.filter(lesson_plan=lesson_match, is_selected=True)
    
    activity_choices = []
    for item in sent_text:
        
        if item[1] in text_results:
            selected = 1
        else:
            selected = 0 
        result = item[1], item[0], selected
        if result not in activity_choices:
            activity_choices.append(result)


    return render(request, 'dashboard/activity_builder_2.html', {'user_profile': user_profile, 'subject_match_full': subject_match_full, 'matched_worksheet': matched_worksheet, 'uploaded_images': uploaded_images, 'activity_choices': activity_choices, 'lesson_analytics': lesson_analytics, 'generated_questions': generated_questions, 'question_lists': question_lists,  'first_topics': first_topics, 'second_topics': second_topics, 'third_topics': third_topics, 'topic_lists_matched': topic_lists_matched, 'sent_text': sent_text,  'match_textlines': match_textlines, 'text_questions': text_questions, 'selected_activities': selected_activities, 'not_selected_activities':not_selected_activities, 'question_list': question_list, 'lessons_wording': lessons_wording, 'question_lists': question_lists, 'text_update': text_update, 'lesson_results': lesson_results, 'topic_lists_selected': topic_lists_selected, 'topic_lists': topic_lists, 'keywords_selected': keywords_selected, 'youtube_matched': youtube_matched, 'questions_selected': questions_selected, 'topics_selected': topics_selected, 'keywords_matched': keywords_matched, 'lesson_standards': lesson_standards, 'lesson_match': lesson_match, 'lesson_activities': lesson_activities, 'class_objectives': class_objectives, 'current_week': current_week, 'classroom_profile': classroom_profile})



def WorksheetBuilder(request, user_id=None, class_id=None, subject=None, lesson_id=None, worksheet_id=None):
    #second step to the standards upload process
    #name="standards_upload"
    matched_lesson = lessonObjective.objects.get(id=lesson_id)
    user_profile = User.objects.filter(username=request.user.username).first()
    matched_worksheet = worksheetFull.objects.get(id=worksheet_id)

    return render(request, 'dashboard/create_worksheet.html', {'user_profile': user_profile, 'matched_worksheet': matched_worksheet})


def CopyPasteLesson(request, user_id=None, class_id=None, subject=None, lesson_id=None):
    #second step to the standards upload process
    #name="standards_upload"
    matched_lesson = lessonObjective.objects.get(id=lesson_id)
    user_profile = User.objects.filter(username=request.user.username).first()

    if request.method == "POST":
        
        form = lessonPDFTextForm(request.POST, request.FILES,)
        if form.is_valid():
            
            prev = form.save()
            get_text_image = pdf_pull_text(prev.id)
            content = get_text_image

            update_text = lessonPDFText.objects.get(id=prev.id)
            update_text.content = content
            update_text.save()
            pdf_image = update_text.pdf_doc.url
            
            pull_images = pdf_pull_images(prev.id, lesson_id, update_text.id)
            return redirect('{}#keywords'.format(reverse('activity_builder', kwargs={'user_id':user_profile.id, 'class_id':class_id, 'subject':subject, 'lesson_id':lesson_id})))
    else:
        data = {'matched_lesson': matched_lesson}
        form = lessonPDFTextForm(initial=data)
        form.fields["matched_lesson"].queryset = lessonObjective.objects.filter(id=lesson_id)
    return render(request, 'dashboard/lesson_image_upload.html', {'user_profile': user_profile, 'form': form})


def LessonImageUpload(request, user_id=None, class_id=None, subject=None, lesson_id=None):
    #second step to the standards upload process
    #name="standards_upload"
    matched_lesson = lessonObjective.objects.get(id=lesson_id)
    user_profile = User.objects.filter(username=request.user.username).first()

    if request.method == "POST":
        form = lessonImageUploadForm(request.POST, request.FILES,)
        if form.is_valid():
            prev = form.save()
            image = prev.image_image.url
            get_text_image = pdf_core(prev.id)
            content = get_text_image

            update_text = lessonImageUpload.objects.get(id=prev.id)
            update_text.content = content
            update_text.save()
            return redirect('{}#keywords'.format(reverse('activity_builder', kwargs={'user_id':user_profile.id, 'class_id':class_id, 'subject':subject, 'lesson_id':lesson_id})))
    else:
        data = {'matched_lesson': matched_lesson}
        form = lessonImageUploadForm(initial=data)
        form.fields["matched_lesson"].queryset = lessonObjective.objects.filter(id=lesson_id)
    return render(request, 'dashboard/lesson_image_upload.html', {'user_profile': user_profile, 'form': form})


def LessonPDFUpload(request, user_id=None, class_id=None, subject=None, lesson_id=None):
    #second step to the standards upload process
    #name="standards_upload"
    current_week = date.today().isocalendar()[1] 
    matched_lesson = lessonObjective.objects.get(id=lesson_id)
    user_profile = User.objects.filter(username=request.user.username).first()

    if request.method == "POST":
        
        form = lessonPDFTextForm(request.POST, request.FILES,)
        if form.is_valid():
            
            prev = form.save()
            
            get_text_image = build_textbook(prev.id, user_id, class_id, lesson_id, current_week)

            return redirect('{}#keywords'.format(reverse('activity_builder', kwargs={'user_id':user_profile.id, 'class_id':class_id, 'subject':subject, 'lesson_id':lesson_id})))
    else:
        data = {'matched_lesson': matched_lesson}
        form = lessonPDFTextForm(initial=data)
        form.fields["matched_lesson"].queryset = lessonObjective.objects.filter(id=lesson_id)
    return render(request, 'dashboard/lesson_image_upload.html', {'user_profile': user_profile, 'form': form})


def PracticeTest(request, user_id=None, class_id=None, subject=None, lesson_id=None):
    current_week = date.today().isocalendar()[1] 
    user_profile = User.objects.get(id=user_id)

    classroom_profile = classroom.objects.get(id=class_id)
    grade_list = classroom_profile.grade_level.all()

    standard_match = standardSet.objects.get(id=classroom_profile.standards_set_id)

    subjects_list = classroom_profile.subjects.all()
    subject_matches = standardSubjects.objects.filter(id__in=subjects_list )                                         
    
    
    class_objectives = lessonObjective.objects.all().order_by('subject')
    vocab_list = vocabularyList.objects.filter(lesson_plan__in=class_objectives)
    lesson_activities = lessonFull.objects.filter(lesson_overview__in=class_objectives)
    lesson_match = lessonObjective.objects.get(id=lesson_id)
    question_match = match_lesson_questions(lesson_match.teacher_objective, class_id, lesson_id)
    lesson_standards = singleStandard.objects.filter(id__in=lesson_match.objectives_standards.all())
    topic_matches = lesson_match.objectives_topics.all()
    topic_lists_selected = topicInformation.objects.filter(id__in=topic_matches).order_by('item')
    topic_count = topic_lists_selected.count()
    chunks = topic_count/3
    one_end = chunks
    two_end = one_end + chunks 
    three_end = two_end + chunks 

    first_topics = topicInformation.objects.filter(id__in=topic_matches).order_by('item')[0:one_end]
    second_topics = topicInformation.objects.filter(id__in=topic_matches).order_by('item')[one_end:two_end]
    third_topics = topicInformation.objects.filter(id__in=topic_matches).order_by('item')[two_end:three_end]

    text_questions = get_question_text(lesson_id)
    text_questions_two_full = get_cluster_text(lesson_id,user_id)
    if text_questions_two_full:
        match_textlines = text_questions_two_full[0]
        topics_selected = text_questions_two_full[1]
        topic_match = text_questions_two_full[2]
    else:
        match_textlines = []
        topics_selected = []
        topic_match = []

    topic_results = []
    for item in topic_match:
        for y in item[2]:
            topic_results.append(y.id)

    topic_lists_matched = topicInformation.objects.filter(id__in=topic_results).order_by('item')

    if match_textlines: 
        summarize_text = summ_text(match_textlines)
        sent_text = get_statment_sent(match_textlines)
    else:
        summarize_text = []
        sent_text = []

    teacher_objective = lesson_match.teacher_objective
    
    lesson_results = []

    questions_selected = googleRelatedQuestions.objects.filter(lesson_plan=lesson_match, is_selected=True)
    topics_selected = googleSearchResult.objects.filter(lesson_plan=lesson_match, is_selected=True)

    keywords_selected = keywordResults.objects.filter(lesson_plan=lesson_match, is_selected=True).order_by('-relevance')
    keywords_matched = keywordResults.objects.filter(lesson_plan=lesson_match, is_selected=False).order_by('-relevance')
    matched_topics = match_topics(teacher_objective, class_id, lesson_id)
    
    text_update, created = lessonText.objects.get_or_create(matched_lesson=lesson_match)
    lessons_wording = text_update.activities
    lesson_activities_matched = get_lessons(lesson_id, user_id)
    
    selected_activities = selectedActivity.objects.filter(lesson_overview=lesson_match, is_selected=True)
    not_selected_activities = selectedActivity.objects.filter(lesson_overview=lesson_match, is_selected=False).order_by('bloom')

    if text_update.activities:
        split_activities = split_matched_activities(text_update.activities, class_id, lesson_id, user_id)

    if text_update.overview:
        split_text = split_matched_text(text_update.overview) 
        split_terms = split_matched_terms(text_update.lesson_terms, class_id, lesson_id) 
        question_list = []
        for line_topic in topic_matches:
            for description_item in line_topic.description.all():
                sentence = line_topic.item + ' - ' + description_item.description
                results = genQuestion(sentence, line_topic.item)
                if results:
                    question_list.append(results)
                else:
                    pass
        text_match = match_lesson_topics(text_update.overview, class_id, lesson_id) 
        
    else:
        split_text = []
        text_match = [] 
        
        question_list = []
    
    
    question_lists = []
    if question_match:
        for item in question_match:
            result_id = item[0][0]
            topic = topicQuestion.objects.get(id=result_id)
    
            question_lists.append(topic )
    
    if question_match:
        pass
    else:
        question_match = []

    combined = matched_topics, text_match
    topic_lists = []
    if combined:
        for text_lists in combined:
            if text_lists:
                for item in text_lists:

                    topic = topicInformation.objects.get(id=item[0][0])

                    word_term = topic.item
                    word_split = word_term.split()
                    word_count = len(word_split)
                    if lesson_match.objectives_topics.filter(id=topic.id).exists():
                        pass
                    else:
                        result = topic, word_count 
                        if result in topic_lists:
                            pass
                        else:
                            topic_lists.append(result)

    topic_lists.sort(key=lambda x: x[1])

    if topic_lists_matched:
        generated_questions = []
        for item in topic_lists_matched:
            generated_quest = generate_questions_topic(item.id)
            if generated_quest:
                generated_questions.append(generated_quest[0])
    else:
        generated_questions = []

    youtube_matched = youtubeSearchResult.objects.filter(lesson_plan=lesson_match, is_selected=True)
    

    
    step = 4

    return render(request, 'dashboard/practice_test.html', {'user_profile': user_profile, 'generated_questions': generated_questions, 'question_lists': question_lists,  'first_topics': first_topics, 'second_topics': second_topics, 'third_topics': third_topics, 'topic_lists_matched': topic_lists_matched, 'sent_text': sent_text,  'topic_match': topic_match, 'match_textlines': match_textlines, 'text_questions': text_questions, 'selected_activities': selected_activities, 'not_selected_activities':not_selected_activities, 'question_list': question_list, 'lessons_wording': lessons_wording, 'question_lists': question_lists, 'text_update': text_update, 'lesson_results': lesson_results, 'topic_lists_selected': topic_lists_selected, 'topic_lists': topic_lists, 'keywords_selected': keywords_selected, 'youtube_matched': youtube_matched, 'questions_selected': questions_selected, 'topics_selected': topics_selected, 'keywords_matched': keywords_matched, 'step': step, 'lesson_standards': lesson_standards, 'lesson_match': lesson_match, 'lesson_activities': lesson_activities, 'class_objectives': class_objectives, 'current_week': current_week, 'classroom_profile': classroom_profile})



def CreateActivity(request, user_id=None, class_id=None, subject=None, lesson_id=None):
    current_week = date.today().isocalendar()[1] 
    user_profile = User.objects.get(id=user_id)

    classroom_profile = classroom.objects.get(id=class_id)
    grade_list = classroom_profile.grade_level.all()

    standard_match = standardSet.objects.get(id=classroom_profile.standards_set_id)
    classroom_subjects = classroom_profile.subjects.all()
    subject_matches = standardSubjects.objects.filter(id__in=classroom_subjects)                                         
    
    lesson_match = lessonObjective.objects.get(id=lesson_id)
    lesson_standards = singleStandard.objects.filter(id__in=lesson_match.objectives_standards.all())
    topic_matches = lesson_match.objectives_topics.all()
    topic_lists_selected = topicInformation.objects.filter(id__in=topic_matches).order_by('item')
    topic_count = topic_lists_selected.count()
    chunks = topic_count/3
    one_end = chunks
    two_end = one_end + chunks 
    three_end = two_end + chunks 

    first_topics = topicInformation.objects.filter(id__in=topic_matches).order_by('item')[0:one_end]
    second_topics = topicInformation.objects.filter(id__in=topic_matches).order_by('item')[one_end:two_end]
    third_topics = topicInformation.objects.filter(id__in=topic_matches).order_by('item')[two_end:three_end]

    text_questions = get_question_text(lesson_id)
    text_questions_two_full = get_cluster_text(lesson_id,user_id)
    if text_questions_two_full:
        match_textlines = text_questions_two_full[0]
        topics_selected = text_questions_two_full[1]
        topic_match = text_questions_two_full[2]

        topic_results = []
        for item in topic_match:
            for y in item:
                topic_results.append(y.id)

        topic_lists_matched = topicInformation.objects.filter(id__in=topic_results).order_by('item')

        summarize_text = summ_text(match_textlines)
        sent_text = get_statment_sent(match_textlines)
    else:
        topic_lists_matched = []
        sent_text = []
        topic_match = []
        match_textlines = []

    teacher_objective = lesson_match.teacher_objective
    
    lesson_results = []

    questions_selected = googleRelatedQuestions.objects.filter(lesson_plan=lesson_match, is_selected=True)
    topics_selected = googleSearchResult.objects.filter(lesson_plan=lesson_match, is_selected=True)

    keywords_selected = keywordResults.objects.filter(lesson_plan=lesson_match, is_selected=True).order_by('-relevance')
    keywords_matched = keywordResults.objects.filter(lesson_plan=lesson_match, is_selected=False).order_by('-relevance')
    matched_topics = match_topics(teacher_objective, class_id, lesson_id)
    
    text_update, created = lessonText.objects.get_or_create(matched_lesson=lesson_match)
    lessons_wording = text_update.activities
    lesson_activities_matched = get_lessons(lesson_id, user_id)
    
    selected_activities = selectedActivity.objects.filter(lesson_overview=lesson_match, is_selected=True)
    not_selected_activities = selectedActivity.objects.filter(lesson_overview=lesson_match, is_selected=False).order_by('bloom')

    if text_update.activities:
        split_activities = split_matched_activities(text_update.activities, class_id, lesson_id, user_id)

    if text_update.overview:
        split_text = split_matched_text(text_update.overview) 
        split_terms = split_matched_terms(text_update.lesson_terms, class_id, lesson_id) 
        question_list = []
        for line_topic in topic_matches:
            for description_item in line_topic.description.all():
                sentence = line_topic.item + ' - ' + description_item.description
                results = genQuestion(sentence, line_topic.item)
                if results:
                    question_list.append(results)
                else:
                    pass
        text_match = match_lesson_topics(text_update.overview, class_id, lesson_id) 
        question_match = match_lesson_questions(text_update.overview, class_id, lesson_id)
    else:
        split_text = []
        text_match = [] 
        question_match = []
        question_list = []
    
    
    question_lists = []
    if question_match:
        for item in question_match:
            topic = topicQuestion.objects.get(id=item[0])
    
            question_lists.append(topic )
    

    combined = matched_topics, text_match
    topic_lists = []
    if combined:
        for text_lists in combined:
            if text_lists:
                for item in text_lists:

                    topic = topicInformation.objects.get(id=item[0][0])

                    word_term = topic.item
                    word_split = word_term.split()
                    word_count = len(word_split)
                    if lesson_match.objectives_topics.filter(id=topic.id).exists():
                        pass
                    else:
                        result = topic, word_count 
                        if result in topic_lists:
                            pass
                        else:
                            topic_lists.append(result)

    topic_lists.sort(key=lambda x: x[1])

    youtube_matched = youtubeSearchResult.objects.filter(lesson_plan=lesson_match, is_selected=True)
    
    if request.method == "POST":
        form = selectedActivityForm(request.POST, request.FILES)

        if form.is_valid():
            prev = form.save(commit=False)
            prev.created_by = user_profile
            prev.lesson_overview = lesson_match
            activity = prev.lesson_text
            matches = label_activities(activity)
            labels = matches[0]
            work = matches[1]
            prev.bloom = labels[1]
            prev.mi = labels[0]
            prev.verb = labels[2]
            prev.is_selected = True
            prev.work_product = work
            prev.save()
        return redirect('{}#keywords'.format(reverse('activity_builder', kwargs={'user_id':user_profile.id, 'class_id':classroom_profile.id, 'subject':subject, 'lesson_id':lesson_id})))
    else:
        form = selectedActivityForm()
    
  
    step = 4
    return render(request, 'dashboard/add_activity.html', {'user_profile': user_profile, 'form': form, 'first_topics': first_topics, 'second_topics': second_topics, 'third_topics': third_topics, 'topic_lists_matched': topic_lists_matched, 'sent_text': sent_text,  'topic_match': topic_match, 'match_textlines': match_textlines, 'text_questions': text_questions, 'selected_activities': selected_activities, 'not_selected_activities':not_selected_activities, 'question_list': question_list, 'lessons_wording': lessons_wording, 'question_lists': question_lists, 'text_update': text_update, 'lesson_results': lesson_results, 'topic_lists_selected': topic_lists_selected, 'topic_lists': topic_lists, 'keywords_selected': keywords_selected, 'youtube_matched': youtube_matched, 'questions_selected': questions_selected, 'topics_selected': topics_selected, 'keywords_matched': keywords_matched, 'step': step, 'lesson_standards': lesson_standards, 'lesson_match': lesson_match, 'current_week': current_week, 'classroom_profile': classroom_profile})



def StandardUploadTwo(request):
    #second step to the standards upload process
    #name="standards_upload"
    template = "administrator/upload_textbook.html"

    prompt = {
        'order': 'Order of the CSV should be first name, surname'   
              }
    # GET request returns the value of the data with the specified key.
    if request.method == "GET":
        return render(request, template, prompt)
    csv_file = request.FILES['file']
    # let's check if it is a csv file
    if not csv_file.name.endswith('.csv'):
        messages.error(request, 'THIS IS NOT A CSV FILE')
    data_set = csv_file.read().decode('UTF-8')
    # setup a stream which is when we loop through each line we are able to handle a data in a stream
    io_string = io.StringIO(data_set)
    next(io_string)
    for line in csv.reader(io_string, delimiter=','):
        standard_set = line[0]
        grade_level = line[1]
        subject = line[2]
        skill_topic = line[3]
        standard_objective = line[4]
        competency = line[5]

        new_standard_set, i = standardSet.objects.get_or_create(Location=standard_set)
        new_grade, i = gradeLevel.objects.get_or_create(grade=grade_level , grade_labels=grade_level , standards_set=new_standard_set)
        new_subject, i = standardSubjects.objects.get_or_create(subject_title=subject, standards_set=new_standard_set, is_admin=True)
        add_grade_subject = new_subject.grade_level.add(new_grade)

        obj, created = singleStandard.objects.get_or_create(standards_set=new_standard_set, subject=new_subject, grade_level=new_grade, skill_topic=skill_topic, standard_objective=standard_objective, competency=competency)

    context = { }
    return render(request, template, context)


def TextbookUploadOne(request):
    #second step to the standards upload process
    #name="standards_upload"

    user_profile = User.objects.filter(username=request.user.username).first()

    if request.method == "POST":
        form = textBookTitleForm(request.POST)
        if form.is_valid():
            prev = form.save()
            return redirect('textbook_uplad_two', textbook_id=prev.id)
    else:
        form = textBookTitleForm()
    return render(request, 'administrator/upload_textbook.html', {'form': form })


def TextbookUploadTwo(request, textbook_id=None):
    #second step to the standards upload process
    #name="standards_upload"
    template = "administrator/upload_textbook.html"
    textbook_match = textBookTitle.objects.get(id=textbook_id)

    prompt = {
        'order': 'Order of the CSV should be first name, surname'   
              }
    # GET request returns the value of the data with the specified key.
    if request.method == "GET":
        return render(request, template, prompt)
    csv_file = request.FILES['file']
    # let's check if it is a csv file
    if not csv_file.name.endswith('.csv'):
        messages.error(request, 'THIS IS NOT A CSV FILE')
    data_set = csv_file.read().decode('UTF-8')
    # setup a stream which is when we loop through each line we are able to handle a data in a stream
    io_string = io.StringIO(data_set)
    next(io_string)

    text_id = textbook_match.id

    for line in csv.reader(io_string, delimiter=','):
        obj, created = textBookBackground.objects.get_or_create(textbook=textbook_match, line_text=line[0], line_lemma=line[1])
        obj.line_counter = int(str(text_id) + str(obj.id)) 
        obj.save()

    update_matches = match_topic_texts(textbook_match.subject, text_id)
    context = {'step': True}
    return render(request, template, context)

def TopicUploadOne(request):
    #second step to the standards upload process
    #name="standards_upload"
    user_profile = User.objects.filter(username=request.user.username).first()

    path3 = 'planit/files/Math_8 - Topics (1).csv'
    with open(path3) as f:
        for line in f:
            line = line.split(',') 
            Subject = line[0]
            Grade_Level = line[1]
            Standard_Set = line[2]
            topic = line[3].title()
            item = line[4].title()
            Description = line[5]
            topic_type = line[6]
            image_name = line[7]
            
           
            standard_match = standardSet.objects.filter(Location=Standard_Set).first()
            matched_grade = gradeLevel.objects.filter(grade=Grade_Level, standards_set=standard_match).first()
            matched_subject = standardSubjects.objects.filter(subject_title=Subject, standards_set=standard_match, grade_level=matched_grade).first()

            topic_match, created = topicTypes.objects.get_or_create(item=topic_type)
            new_topic, created = topicInformation.objects.get_or_create(subject=matched_subject, grade_level=matched_grade, standard_set=standard_match, topic=topic, item=item, description=Description, image_name=image_name)

            add_topic = new_topic.topic_type.add(topic_match)
            
        
    return redirect('Dashboard', week_of='Current')
    
def TopicUploadTwo(request):
    #second step to the standards upload process
    #name="standards_upload"
    template = "administrator/upload_textbook.html"


    prompt = {
        'order': 'Order of the CSV should be first name, surname'   
              }
    # GET request returns the value of the data with the specified key.
    if request.method == "GET":
        return render(request, template, prompt)
    csv_file = request.FILES['file']
    # let's check if it is a csv file
    if not csv_file.name.endswith('.csv'):
        messages.error(request, 'THIS IS NOT A CSV FILE')
    data_set = csv_file.read().decode('UTF-8')
    # setup a stream which is when we loop through each line we are able to handle a data in a stream
    io_string = io.StringIO(data_set)
    next(io_string)

    for line in csv.reader(io_string, delimiter=','):
        Subject = line[0]
        Grade_Level = line[1]
        Standard_Set = line[2]
        topic = line[3]
        item = line[4]
        Description = line[5]
        topic_type = line[6]
        image_name = line[7]
        
        standard_match = standardSet.objects.filter(Location=Standard_Set).first()
        matched_grade = gradeLevel.objects.filter(grade=Grade_Level, standards_set=standard_match).first()
        matched_subject = standardSubjects.objects.filter(subject_title=Subject, standards_set=standard_match, grade_level=matched_grade).first()
        topic_match, created = topicTypes.objects.get_or_create(item=topic_type)
        new_topic, created = topicInformation.objects.get_or_create(subject=matched_subject, grade_level=matched_grade, standard_set=standard_match, topic=topic, item=item, image_name=image_name)
        new_description, created =  topicDescription.objects.get_or_create(description=Description) 
        add_description = new_topic.description.add(new_description)
        add_topic = new_topic.topic_type.add(topic_match)

    context = {'step': True}
    return render(request, template, context)


def TopicUploadTwo(request):
    #second step to the standards upload process
    #name="standards_upload"
    template = "administrator/upload_textbook.html"


    prompt = {
        'order': 'Order of the CSV should be first name, surname'   
              }
    # GET request returns the value of the data with the specified key.
    if request.method == "GET":
        return render(request, template, prompt)
    csv_file = request.FILES['file']
    # let's check if it is a csv file
    if not csv_file.name.endswith('.csv'):
        messages.error(request, 'THIS IS NOT A CSV FILE')
    data_set = csv_file.read().decode('UTF-8')
    # setup a stream which is when we loop through each line we are able to handle a data in a stream
    io_string = io.StringIO(data_set)
    next(io_string)

    for line in csv.reader(io_string, delimiter=','):
        Subject = line[0]
        Grade_Level = line[1]
        Standard_Set = line[2]
        topic = line[3]
        item = line[4]
        Description = line[5]
        topic_type = line[6]
        image_name = line[7]
        
        standard_match = standardSet.objects.filter(Location=Standard_Set).first()
        matched_grade = gradeLevel.objects.filter(grade=Grade_Level, standards_set=standard_match).first()
        matched_subject = standardSubjects.objects.filter(subject_title=Subject, standards_set=standard_match, grade_level=matched_grade).first()
        topic_match, created = topicTypes.objects.get_or_create(item=topic_type)
        new_topic, created = topicInformation.objects.get_or_create(subject=matched_subject, grade_level=matched_grade, standard_set=standard_match, topic=topic, item=item, image_name=image_name)
        new_description, created =  topicDescription.objects.get_or_create(description=Description) 
        add_description = new_topic.description.add(new_description)
        add_topic = new_topic.topic_type.add(topic_match)

    context = {'step': True}
    return render(request, template, context)

def generate_studyguide_pdf(request):

    people = 'Audrey'

    # Rendered
    html_string = render_to_string('dashboard/pdf.html', {'people': people})
    html = HTML(string=html_string, base_url=request.build_absolute_uri('/'))
    result = html.write_pdf()

     # Creating http response
    response = HttpResponse(content_type='application/pdf;')
    response['Content-Disposition'] = 'inline; filename=list_people.pdf'
    response['Content-Transfer-Encoding'] = 'binary'
    with tempfile.NamedTemporaryFile(delete=True) as output:
         output.write(result)
         output.flush()
         output = open(output.name, 'rb')
         response.write(output.read())

    return response


def generate_lesson_pdf(request, lesson_id):


    lesson_match = lessonObjective.objects.get(id=lesson_id)
    # Rendered
    text_update = lessonText.objects.get(matched_lesson=lesson_match)
    html_string = render_to_string('dashboard/lesson_pdf.html', {'text_update': text_update})
    html = HTML(string=html_string, base_url=request.build_absolute_uri('/'))
    result = html.write_pdf()

     # Creating http response
    response = HttpResponse(content_type='application/pdf;')
    response['Content-Disposition'] = 'inline; filename=Lesson_Plan.pdf'
    response['Content-Transfer-Encoding'] = 'binary'
    with tempfile.NamedTemporaryFile(delete=True) as output:
         output.write(result)
         output.flush()
         output = open(output.name, 'rb')
         response.write(output.read())

    return response

def DigitalWorksheet(request, user_id=None, class_id=None, subject=None, lesson_id=None):
    current_week = date.today().isocalendar()[1] 
    user_profile = User.objects.get(id=user_id)

    classroom_profile = classroom.objects.get(id=class_id)
    grade_list = classroom_profile.grade_level.all()

    standard_match = standardSet.objects.get(id=classroom_profile.standards_set_id)
    classroom_subjects = classroom_profile.subjects.all()

    subject_matches = standardSubjects.objects.filter(id__in=classroom_subjects)                                         
                                             
    
    lesson_match = lessonObjective.objects.get(id=lesson_id)
    topic_matches = lesson_match.objectives_topics.all()
    lesson_standards = singleStandard.objects.filter(id__in=lesson_match.objectives_standards.all())
    topic_lists_selected = topicInformation.objects.filter(id__in=topic_matches).order_by('item')

    if topic_lists_selected:
        generated_questions = []
        for item in topic_lists_selected:
            generated_quest = generate_questions_topic(item.id)
            if generated_quest:
                generated_questions.append(generated_quest[0])
    else:
        generated_questions = []

    return render(request, 'dashboard/worksheet_builder.html', {'user_profile': user_profile, 'lesson_match': lesson_match, 'generated_questions': generated_questions })




def DigitalStudyGuide(request, user_id=None, class_id=None, subject=None, lesson_id=None):
    current_week = date.today().isocalendar()[1] 
    user_profile = User.objects.get(id=user_id)

    classroom_profile = classroom.objects.get(id=class_id)
    grade_list = classroom_profile.grade_level.all()

    standard_match = standardSet.objects.get(id=classroom_profile.standards_set_id)
    classroom_subjects = classroom_profile.subjects.all()

    subject_matches = standardSubjects.objects.filter(id__in=classroom_subjects)                                         
    
    
    class_objectives = lessonObjective.objects.all().order_by('subject')
    vocab_list = vocabularyList.objects.filter(lesson_plan__in=class_objectives)
    lesson_activities = lessonFull.objects.filter(lesson_overview__in=class_objectives)
    lesson_match = lessonObjective.objects.get(id=lesson_id)
    lesson_standards = singleStandard.objects.filter(id__in=lesson_match.objectives_standards.all())
    topic_matches = lesson_match.objectives_topics.all()
    topic_list = topicInformation.objects.filter(id__in=topic_matches)
    teacher_objective = lesson_match.teacher_objective
   
    questions_selected = googleRelatedQuestions.objects.filter(lesson_plan=lesson_match, is_selected=True)
    topics_selected = googleSearchResult.objects.filter(lesson_plan=lesson_match, is_selected=True)
    

    keywords_selected = keywordResults.objects.filter(lesson_plan=lesson_match, is_selected=True).order_by('-relevance')
    keywords_matched = keywordResults.objects.filter(lesson_plan=lesson_match, is_selected=False).order_by('-relevance')

    keywords = []
    
    youtube_matched = youtubeSearchResult.objects.filter(lesson_plan=lesson_match, is_selected=True)
    

    return render(request, 'dashboard/study_guide.html', {'user_profile': user_profile, 'topic_list': topic_list, 'keywords_selected': keywords_selected, 'youtube_matched': youtube_matched, 'questions_selected': questions_selected, 'topics_selected': topics_selected, 'keywords_matched': keywords_matched, 'lesson_standards': lesson_standards, 'lesson_match': lesson_match, 'lesson_activities': lesson_activities, 'class_objectives': class_objectives, 'current_week': current_week, 'classroom_profile': classroom_profile})



def QuestionUploadTwo(request):
    #second step to the standards upload process
    #name="standards_upload"
    template = "administrator/upload_textbook.html"


    prompt = {
        'order': 'Order of the CSV should be first name, surname'   
              }
    # GET request returns the value of the data with the specified key.
    if request.method == "GET":
        return render(request, template, prompt)
    csv_file = request.FILES['file']
    # let's check if it is a csv file
    if not csv_file.name.endswith('.csv'):
        messages.error(request, 'THIS IS NOT A CSV FILE')
    data_set = csv_file.read().decode('UTF-8')
    # setup a stream which is when we loop through each line we are able to handle a data in a stream
    io_string = io.StringIO(data_set)
    next(io_string)

    for line in csv.reader(io_string, delimiter=','):
        subject	= line[0]
        grade_level = line[1]	
        standard_set = line[2]
        topic_type = line[3]	
        item = line[4] 	
        question_type = line[5]  
        question_points = 1		
        Question = line[6] 		
        Correct	= line[8] 	
        Incorrect_One = line[10] 	
        Incorrect_Two = line[12] 		
        Incorrect_Three	= line[14] 
        Story = line[15]
        explanation	= line[16]
        
        
        if Story:
            add_story, created = storySection.objects.get_or_create(Section=Story)
            q_title = str(Question) + '-' + str(subject) + str(add_story.id)
            add_full, created = storyFull.objects.get_or_create(Title=q_title)
            new_story = add_full.section.add(add_story)

        item = get_keywords(Question)
        standard_match = standardSet.objects.filter(Location=standard_set).first()
        matched_grade = gradeLevel.objects.filter(grade=grade_level, standards_set=standard_match).first()
        matched_subject = standardSubjects.objects.filter(subject_title=subject, standards_set=standard_match, grade_level=matched_grade).first()
        topic_match, created = topicTypes.objects.get_or_create(item=topic_type)
        question_type, created = questionType.objects.get_or_create(item=question_type)

        new_question, created = topicQuestion.objects.get_or_create(subject=matched_subject, grade_level=matched_grade, standard_set=standard_match, item=item, question_type=question_type, question_points=question_points, Question=Question, Correct=Correct, Incorrect_One=Incorrect_One, Incorrect_Two=Incorrect_Two, Incorrect_Three=Incorrect_Three, explanation=explanation )

        add_topic = new_question.topic_type.add(topic_match)
        if add_full:
            add_new_story = new_question.topic_story.add(add_full)

    context = {'step': True}
    return render(request, template, context)


