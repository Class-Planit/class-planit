from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View, FormView, TemplateView, DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect



# Create your views here.
class Homepage(TemplateView):
    template_name = 'index.html'
    


class GetStarted(TemplateView):
    template_name = 'index-04.html'
    