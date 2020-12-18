from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View, FormView, TemplateView, DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic.edit import FormMixin
from django.template.loader import render_to_string
import _datetime
from datetime import datetime
import fitz
import PyPDF2  

from django.db.models import Q
from weasyprint import HTML
from .generation import *
import tempfile
from .models import *
from .forms import *
from .match_standards import *

# Create your views here.
class Homepage(TemplateView):
    template_name = 'index.html'    






class FormListView(FormMixin):
    def get(self, request, *args, **kwargs):
        # From ProcessFormMixin
        form_class = self.get_form_class()
        self.form = self.get_form(form_class)

        context = self.get_context_data(form=self.form)
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)



def Signup(request):

    if request.method == "POST":
        form = SignUpForm(request.POST)
        
        if form.is_valid():
            prev = form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)

            return redirect('my_profile', user_id=user.id)

    else:

        form = SignUpForm()

    return render(request, 'signup_form.html', {'form': form, })


def MyProfile(request, user_id=None):
    user_profile = User.objects.get(id=user_id)
    classrooms_matches = classroom.objects.filter(main_teacher=user_profile)
    shared_classrooms = classroom.objects.filter(support_teachers=user_profile)

    return render(request, 'profile_summary.html', {'user_profile': user_profile, 'classrooms_matches': classrooms_matches, 'shared_classrooms': shared_classrooms })


def SingleClassroom(request, user_id=None, class_id=None):
    user_profile = User.objects.get(id=user_id)
    classroom = Classroom.objects.get(id=class_id)

    return render(request, 'profile_summary.html', {'user_profile': user_profile, 'classroom': classroom })


def ProfileSettings(request, user_id=None):
    user_profile = User.objects.get(id=user_id)
    academic_year = academicYear.objects.filter(is_active=True).first()
    current_date = _datetime.date.today()
    standards_sets = standardSet.objects.all()
    

    if 'New' in class_id:
        classroom = []
        if request.method == "POST":
            form1 = academicYearForm(request.POST, request.FILES)
            form2 = ClassroomForm(request.POST, request.FILES)
            print(form2)
            if form1.is_valid():
                form1.save()
                return redirect('my_profile', user_id=user_profile.id)

            if form2.is_valid():
                prev = form2.save(commit=False)
                prev.academic_year = academic_year
                prev.planning_teacher = user_profile
                prev.save()
                return redirect('my_profile', user_id=user_profile.id)
        else:
            if academic_year:
                form1 = academicYearForm(instance=academic_year)
            else:
                data = {'planning_teacher': user_profile,
                        'start_date': current_date}
                form1 = academicYearForm(initial=data)
                
            form2_data = {'main_teacher': user_profile}
            form2 = ClassroomForm(initial=form2_data)
    else:
        classroom = Classroom.objects.get(id=class_id)
        if request.method == "POST":
            if academic_year:
                form1 = academicYearForm(request.POST, request.FILES, instance=academic_year)
            else:
                form1 = academicYearForm(request.POST, request.FILES)

            form2 = ClassroomForm(request.POST, request.FILES, instance=classroom)
            if form1.is_valid():
                form1.save()
                return redirect('my_profile', user_id=user_profile.id)
            if form2.is_valid():
                prev = form2.save(commit=False)
                prev.academic_year = academic_year
                prev.save()
                return redirect('my_profile', user_id=user_profile.id)
        else:
            if academic_year:
                form1 = academicYearForm(instance=academic_year)
            else:
                data = {'planning_teacher': user_profile,
                        'start_date': current_date}
                form1 = academicYearForm(initial=data)

            form2 = ClassroomForm(instance=classroom)

    return render(request, 'classroom_settings.html', {'user_profile': user_profile, 'classroms_matches': classroms_matches, 'shared_classrooms': shared_classrooms, 'standards_sets': standards_sets, 'classroom': classroom, 'form1': form1, 'form2': form2 })

def ClassroomSettings(request, user_id=None, class_id=None, edit=None):
    user_profile = User.objects.get(id=user_id)
    academic_year = academicYear.objects.filter(is_active=True).first()
    current_date = _datetime.date.today()
    standards_sets = standardSet.objects.all()


    

    if 'New' in class_id:
        classroom_profile = []
        grade_summary = []
        class_subjects = []
        class_subjects_list = []
        standards_subjects = []

        if request.method == "POST":
            
            form2 = ClassroomForm(request.POST, request.FILES)

            if form2.is_valid():
                prev = form2.save(commit=False)
                prev.academic_year = academic_year
                prev.main_teacher = user_profile
                prev.save()
                return redirect('classroom_settings', user_id=user_profile.id, class_id=classroom_profile.id, edit=0)
        else:

            form2_data = {'main_teacher': user_profile}
            form2 = ClassroomForm(initial=form2_data)
        

    else:
        edit = int(edit)
        classroom_profile = classroom.objects.get(id=class_id)
        class_grades = classroom_profile.grade_level.all()
        standards = classroom_profile.standards_set
        grade_level_matches = gradeLevel.objects.filter(standards_set=standards)

        grade_summary = []

        for grade in grade_level_matches:
            if grade in class_grades:
                result = grade, True
            else:
                result = grade, False
            if result in grade_summary:
                pass
            else:
                grade_summary.append(result)

        class_subjects = classroomSubjects.objects.filter(subject_classroom=classroom_profile).first()
        class_subjects_list = class_subjects.subjects.all()
        standards_subjects = standardSubjects.objects.filter(standards_set=standards).exclude(id__in=class_subjects_list)
        


        if edit == 1:
            if request.method == "POST":

                form2 = ClassroomForm(request.POST, request.FILES, instance=classroom_profile)

                if form2.is_valid():
                    prev = form2.save(commit=False)
                    prev.academic_year = academic_year
                    prev.save()
                    return redirect('classroom_settings', user_id=user_profile.id, class_id=classroom_profile.id, edit=0)
            else:

                form2 = ClassroomForm(instance=classroom_profile)
        else:
            form2 = []

    return render(request, 'classroom_settings.html', {'user_profile': user_profile, 'class_subjects_list': class_subjects_list, 'standards_subjects': standards_subjects, 'grade_summary': grade_summary, 'edit': edit, 'standards_sets': standards_sets, 'classroom_profile': classroom_profile, 'form2': form2 })

def UpdateGradeLevel(request, user_id=None, class_id=None, grade_id=None, action=None):
    user_profile = User.objects.get(id=user_id)
    classroom_profile = classroom.objects.get(id=class_id)
    subject_match = gradeLevel.objects.get(id=grade_id)
    action = int(action)
    if action == 0:
        classroom_profile.grade_level.add(grade_match)
    else:
        classroom_profile.grade_level.remove(grade_match)
    return redirect('{}#grade_level'.format(reverse('classroom_settings', kwargs={'user_id':user_profile.id, 'class_id':classroom_profile.id, 'edit':0})))

def UpdateClassSubject(request, user_id=None, class_id=None, subject_id=None, action=None):
    user_profile = User.objects.get(id=user_id)
    classroom_profile = classroom.objects.get(id=class_id)
    
    subject_match = standardSubjects.objects.get(id=subject_id)
    action = int(action)
    if action == 0:
        add_subject, created = classroomSubjects.objects.get_or_create(subject_classroom=classroom_profile)
        add_subject.subjects.add(subject_match)

    else:
        subject_info = classroomSubjects.objects.filter(subject_classroom=classroom_profile).first()
        subject_info.subjects.remove(subject_match)
    return redirect('{}#subjects'.format(reverse('classroom_settings', kwargs={'user_id':user_profile.id, 'class_id':classroom_profile.id, 'edit':0})))


def ClassroomPlanbook(request, user_id=None, class_id=None, subject=None):
    current_week = date.today().isocalendar()[1] 
    user_profile = User.objects.get(id=user_id)

    classroom_profile = classroom.objects.get(id=class_id)
    grade_list = classroom_profile.grade_level.all()

    standard_match = standardSet.objects.get(id=classroom_profile.standards_set_id)
    classroom_subjects = classroomSubjects.objects.filter(subject_classroom=classroom_profile).first()
    subjects_list = classroom_subjects.subjects.all()
    subject_matches = standardSubjects.objects.filter(id__in=classroom_subjects.subjects.all())
    class_objectives = lessonObjective.objects.all().order_by('subject')
    vocab_list = vocabularyList.objects.filter(lesson_plan__in=class_objectives)
    lesson_activities = lessonFull.objects.filter(lesson_overview__in=class_objectives)



    if request.method == "POST":
        form = lessonObjectiveForm(request.POST, request.FILES)

        if form.is_valid():
            prev = form.save(commit=False)
            prev.lesson_classroom = classroom_profile
            prev.week_of = current_week
            teacher_objective = prev.teacher_objective
            subject = prev.subject_id
            grades = grade_list 
            prev.save()
           
            return redirect('select_standards', user_id=user_profile.id, class_id=classroom_profile.id, subject=subject, lesson_id=prev.id)
    else:
        form = lessonObjectiveForm()
    return render(request, 'planbook.html', {'user_profile': user_profile, 'subject_matches': subject_matches, 'lesson_activities': lesson_activities, 'class_objectives': class_objectives, 'vocab_list': vocab_list, 'current_week': current_week, 'form': form, 'subjects_list': subjects_list, 'grade_list': grade_list, 'classroom_profile': classroom_profile, 'classroom_subjects': classroom_subjects})


def SelectStandards(request, user_id=None, class_id=None, subject=None, lesson_id=None):
    current_week = date.today().isocalendar()[1] 
    user_profile = User.objects.get(id=user_id)

    classroom_profile = classroom.objects.get(id=class_id)
    grade_list = classroom_profile.grade_level.all()

    standard_match = standardSet.objects.get(id=classroom_profile.standards_set_id)
    classroom_subjects = classroomSubjects.objects.filter(subject_classroom=classroom_profile).first()
    subjects_list = classroom_subjects.subjects.all()
    subject_matches = standardSubjects.objects.filter(id__in=classroom_subjects.subjects.all())
    current_subject = standardSubjects.objects.get(id=subject)
    
    class_objectives = lessonObjective.objects.all().order_by('subject')
    vocab_list = vocabularyList.objects.filter(lesson_plan__in=class_objectives)
    lesson_activities = lessonFull.objects.filter(lesson_overview__in=class_objectives)
    lesson_match = lessonObjective.objects.get(id=lesson_id)
    current_standards = singleStandard.objects.filter(id__in=lesson_match.objectives_standards.all())
    teacher_objective = lesson_match.teacher_objective
    

    recomendations = lessonStandardRecommendation.objects.filter(lesson_classroom=classroom_profile, objectives=lesson_match)
    
    results = match_standard(teacher_objective, current_subject, class_id)
    
    for item in results:
        grade = item[0]
        standards = item[1]
        for standard in standards:
            standard_id = standard[0]
            standard_match = singleStandard.objects.filter(id=standard_id).first()
            create_objective, created = lessonStandardRecommendation.objects.get_or_create(lesson_classroom=classroom_profile, objectives=lesson_match, objectives_standard=standard_match)   

    step = 1
    return render(request, 'create_objective.html', {'user_profile': user_profile, 'step': step, 'current_standards': current_standards, 'recomendations': recomendations, 'lesson_match': lesson_match, 'subject_matches': subject_matches, 'lesson_activities': lesson_activities, 'class_objectives': class_objectives, 'vocab_list': vocab_list, 'current_week': current_week, 'subjects_list': subjects_list, 'grade_list': grade_list, 'classroom_profile': classroom_profile, 'classroom_subjects': classroom_subjects})

def SelectKeywords(request, user_id=None, class_id=None, subject=None, lesson_id=None):
    current_week = date.today().isocalendar()[1] 
    user_profile = User.objects.get(id=user_id)

    classroom_profile = classroom.objects.get(id=class_id)
    grade_list = classroom_profile.grade_level.all()

    standard_match = standardSet.objects.get(id=classroom_profile.standards_set_id)
    classroom_subjects = classroomSubjects.objects.filter(subject_classroom=classroom_profile).first()
    subjects_list = classroom_subjects.subjects.all()
    subject_matches = standardSubjects.objects.filter(id__in=classroom_subjects.subjects.all())
    
    
    class_objectives = lessonObjective.objects.all().order_by('subject')
    vocab_list = vocabularyList.objects.filter(lesson_plan__in=class_objectives)
    lesson_activities = lessonFull.objects.filter(lesson_overview__in=class_objectives)
    lesson_match = lessonObjective.objects.get(id=lesson_id)
    lesson_standards = singleStandard.objects.filter(id__in=lesson_match.objectives_standards.all())
    teacher_objective = lesson_match.teacher_objective

    related_question = googleRelatedQuestions.objects.filter(lesson_plan=lesson_match, is_selected=False)
    related_topics = googleSearchResult.objects.filter(lesson_plan=lesson_match, is_selected=False)
   
    questions_selected = googleRelatedQuestions.objects.filter(lesson_plan=lesson_match, is_selected=True)
    topics_selected = googleSearchResult.objects.filter(lesson_plan=lesson_match, is_selected=True)
    selected_wiki = wikiTopic.objects.filter(lesson_plan=lesson_match, is_selected=True)

    wiki_topics = wikiTopic.objects.filter(lesson_plan=lesson_match).exclude(is_selected=True).order_by('-relevance')

    
    if lesson_match.is_skill:
        results = google_results(teacher_objective, lesson_id)
    else:
        results = wiki_google_results(teacher_objective, lesson_id)
    
    
    
  
    step = 2
    return render(request, 'create_objective.html', {'user_profile': user_profile, 'selected_wiki': selected_wiki, 'questions_selected': questions_selected, 'topics_selected': topics_selected,  'related_question': related_question, 'related_topics': related_topics, 'wiki_topics': wiki_topics, 'step': step, 'lesson_standards': lesson_standards, 'lesson_match': lesson_match, 'lesson_activities': lesson_activities, 'class_objectives': class_objectives, 'current_week': current_week, 'classroom_profile': classroom_profile})



def SelectKeywordsTwo(request, user_id=None, class_id=None, subject=None, lesson_id=None):
    current_week = date.today().isocalendar()[1] 
    user_profile = User.objects.get(id=user_id)

    classroom_profile = classroom.objects.get(id=class_id)
    grade_list = classroom_profile.grade_level.all()

    standard_match = standardSet.objects.get(id=classroom_profile.standards_set_id)
    classroom_subjects = classroomSubjects.objects.filter(subject_classroom=classroom_profile).first()
    subjects_list = classroom_subjects.subjects.all()
    subject_matches = standardSubjects.objects.filter(id__in=classroom_subjects.subjects.all())
    
    
    class_objectives = lessonObjective.objects.all().order_by('subject')
    vocab_list = vocabularyList.objects.filter(lesson_plan__in=class_objectives)
    lesson_activities = lessonFull.objects.filter(lesson_overview__in=class_objectives)
    lesson_match = lessonObjective.objects.get(id=lesson_id)
    lesson_standards = singleStandard.objects.filter(id__in=lesson_match.objectives_standards.all())
    teacher_objective = lesson_match.teacher_objective



    questions_selected = googleRelatedQuestions.objects.filter(lesson_plan=lesson_match, is_selected=True)
    topics_selected = googleSearchResult.objects.filter(lesson_plan=lesson_match, is_selected=True)

    keywords_selected = keywordResults.objects.filter(lesson_plan=lesson_match, is_selected=True).order_by('-relevance')
    keywords_matched = keywordResults.objects.filter(lesson_plan=lesson_match, is_selected=False).order_by('-relevance')

    keywords = get_lesson_keywords(lesson_id)
    
    
    
  
    step = 3
    return render(request, 'create_objective.html', {'user_profile': user_profile, 'keywords_selected': keywords_selected, 'questions_selected': questions_selected, 'topics_selected': topics_selected, 'keywords_matched': keywords_matched, 'step': step, 'lesson_standards': lesson_standards, 'lesson_match': lesson_match, 'lesson_activities': lesson_activities, 'class_objectives': class_objectives, 'current_week': current_week, 'classroom_profile': classroom_profile})


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


def EditObjectiveStandards(request, user_id=None, class_id=None, subject=None, lesson_id=None, standard_id=None, action=None):
    user_profile = User.objects.get(id=user_id)
    classroom_profile = classroom.objects.get(id=class_id)
    lesson_match = lessonObjective.objects.get(id=lesson_id)
    standard_match = singleStandard.objects.get(id=standard_id)
    recomendations = lessonStandardRecommendation.objects.get(lesson_classroom=classroom_profile, objectives_standard=standard_id, objectives=lesson_match )
    action = int(action)
    if action == 0:
        lesson_match.objectives_standards.add(standard_match)
        recomendations.is_selected = True
        recomendations.save()
    else:
        lesson_match.objectives_standards.remove(standard_match)
        recomendations.is_selected = False
        recomendations.save()
    return redirect('{}#standards'.format(reverse('select_standards', kwargs={'user_id':user_profile.id, 'class_id':classroom_profile.id, 'subject':subject, 'lesson_id':lesson_id})))


def CreateVocabularyWord(request, user_id=None, class_id=None, lesson_id=None):
    user_profile = User.objects.get(id=user_id)

    classroom_profile = classroom.objects.get(id=class_id)
    class_objectives = lessonObjective.objects.get(id=lesson_id)
    vocab_list = vocabularyList.objects.filter(lesson_plan=class_objectives)
    

    if request.method == "POST":
        update_list, i = vocabularyList.objects.get_or_create(lesson_plan=class_objectives)

        form2 = vocabularyWordForm(request.POST, request.FILES)

        if form2.is_valid():
            prev = form2.save(commit=False)
            word = prev.word
            results = get_vocab_context(word)
            prev.p_o_s = results[2]
            prev.definition = results[0]
            prev.sentence = results[1]
            
            prev.save()
            add_word = update_list.vocab_words.add(prev)

        return redirect('classroom_planbook', user_id=user_profile.id, class_id=classroom_profile.id, subject='All')
    else:
        form2 = vocabularyWordForm()
    return render(request, 'vocabulary_lists.html', {'user_profile': user_profile, 'form2': form2, 'vocab_list': vocab_list, 'classroom_profile': classroom_profile })


def CreateSingleLesson(request, user_id=None, class_id=None, lesson_id=None):
    user_profile = User.objects.get(id=user_id)

    classroom_profile = classroom.objects.get(id=class_id)
    class_objectives = lessonObjective.objects.get(id=lesson_id)
    subject = class_objectives.subject
    lesson_match = lessonFull.objects.filter(lesson_overview=class_objectives).first()
    
    if lesson_match:
        lesson_section = lesson_match.lesson_section.all()
        wiki_results = get_questions(class_objectives.id, lesson_match.id)
        g_result = wiki_results[0]
        wiki = wiki_results[1]
        definitions = wiki_results[2]
        youtube = wiki_results[3]
        section_matches = lessonSection.objects.filter(id__in=lesson_section).order_by('order_num')
    else:
        lesson_section = []
        wiki = []
        definitions = []
        section_matches = []
        youtube = []
        g_result = []


    if request.method == "POST":
        full_lesson, i = lessonFull.objects.get_or_create(lesson_overview=class_objectives, subject=subject)
        form2 = lessonSectionForm(request.POST, request.FILES)

        if form2.is_valid():
            prev = form2.save(commit=False)
            title = prev.title
            prev.save()
            add_section = full_lesson.lesson_section.add(prev)
            if full_lesson.title:
                pass
            else:
                full_lesson.title = title
                full_lesson.save()
        return redirect('classroom_lesson', user_id=user_profile.id, class_id=classroom_profile.id, lesson_id=lesson_id)
    else:
        form2 = lessonSectionForm()
    return render(request, 'lesson_builder.html', {'user_profile': user_profile, 'definitions': definitions, 'youtube': youtube, 'wiki': wiki, 'g_result': g_result, 'lesson_match': lesson_match, 'section_matches': section_matches, 'form2': form2, 'classroom_profile': classroom_profile })



def ClassroomStudents(request, user_id=None, class_id=None, student_id=None):
    user_profile = User.objects.get(id=user_id)

    classroom_profile = classroom.objects.get(id=class_id)
    
    return render(request, 'students.html', {'user_profile': user_profile, 'classroom_profile': classroom_profile })


def ClassroomAnalytics(request, user_id=None, class_id=None, subject=None):
    user_profile = User.objects.get(id=user_id)

    classroom_profile = Classroom.objects.get(id=class_id)

    return render(request, 'analytics.html', {'user_profile': user_profile, 'classroom_profile': classroom_profile })


def ClassroomAssignments(request, user_id=None, class_id=None, subject=None):
    user_profile = User.objects.get(id=user_id)

    classroom_profile = classroom.objects.get(id=class_id)

    return render(request, 'assignments.html', {'user_profile': user_profile, 'classroom_profile': classroom_profile })


class GetStarted(TemplateView):

    template_name = 'index-04.html'
    
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        #text = context['text'] = 'William Shakespeare (bapt. 26 April 1564 – 23 April 1616)[a] was an English playwright, poet, and actor, widely regarded as the greatest writer in the English language and the world greatest dramatist. He is often called England national poet and the "Bard of Avon" (or simply "the Bard").[5][b] His extant works, including collaborations, consist of some 39 plays,[c] 154 sonnets, two long narrative poems, and a few other verses, some of uncertain authorship. His plays have been translated into every major living language and are performed more often than those of any other playwright.[7] They also continue to be studied and reinterpreted.'
        #context['results'] = get_question_and_answer(text)
        
        return context



def generate_pdf(request):
    ## This is the text pdf generation that will be used for worksheets and reports 
    """Generate pdf."""
    # Model data
    people = 'Audrey'

    # Rendered
    html_string = render_to_string('pdf.html', {'people': people})
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





def StandardUploadTwo(request):
    #second step to the standards upload process
    #name="standards_upload"
    user_profile = User.objects.filter(username=request.user.username).first()

    path3 = 'planit/pdf_files/teks_final.csv'
    with open(path3) as f:
        for line in f:
            line = line.split(',') 
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

    return redirect('my_profile', user_id=user_profile.id)



