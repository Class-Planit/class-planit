from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View, FormView, TemplateView, DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic.edit import FormMixin
from django.template.loader import render_to_string
from weasyprint import HTML
from .generation import *
import tempfile
from .models import *
from .forms import *

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


    return render(request, 'profile_summary.html', {'user_profile': user_profile, })


def SingleClassroom(request, user_id=None, class_id=None):
    user_profile = User.objects.get(id=user_id)
    classroom = Classroom.objects.get(id=class_id)

    return render(request, 'profile_summary.html', {'user_profile': user_profile, 'classroom': classroom })

def ClassroomSettings(request, user_id=None, class_id=None):
    user_profile = User.objects.get(id=user_id)

    if 'New' in class_id:
        classroom = []
        if request.method == "POST":
            form2 = ClassroomForm(request.POST, request.FILES,)
            if form2.is_valid():
                form2.save()
                return redirect('my_profile', user_id=user_profile.id)
        else:
            form2 = ClassroomForm()
    else:
        classroom = Classroom.objects.get(id=class_id)
        if request.method == "POST":
            form2 = ClassroomForm(request.POST, request.FILES, instance=classroom)
            if form2.is_valid():
                form2.save()
                return redirect('my_profile', user_id=user_profile.id)
        else:
            form2 = ClassroomForm(instance=classroom)
    return render(request, 'classroom_settings.html', {'user_profile': user_profile, 'classroom': classroom, 'form2': form2 })


def ClassroomPlanbook(request, user_id=None, class_id=None, subject=None):
    user_profile = User.objects.get(id=user_id)

    classroom = Classroom.objects.get(id=class_id)

    return render(request, 'planbook.html', {'user_profile': user_profile, 'classroom': classroom })


def ClassroomStudents(request, user_id=None, class_id=None, student_id=None):
    user_profile = User.objects.get(id=user_id)

    classroom = Classroom.objects.get(id=class_id)

    return render(request, 'students.html', {'user_profile': user_profile, 'classroom': classroom })


def ClassroomAnalytics(request, user_id=None, class_id=None, subject=None):
    user_profile = User.objects.get(id=user_id)

    classroom = Classroom.objects.get(id=class_id)

    return render(request, 'analytics.html', {'user_profile': user_profile, 'classroom': classroom })


def ClassroomAssignments(request, user_id=None, class_id=None, subject=None):
    user_profile = User.objects.get(id=user_id)

    classroom = Classroom.objects.get(id=class_id)

    return render(request, 'assignments.html', {'user_profile': user_profile, 'classroom': classroom })


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