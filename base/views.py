

from django.shortcuts import render, redirect
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.urls import reverse_lazy #To redirect the user to a certain page
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin #it means if user is not logged in redirect him to log in page
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.views import View
from django.shortcuts import redirect
from django.db import transaction
from .models import Task
from .forms import PositionForm

class CustomLoginView(LoginView):
    template_name = 'base/login.html'
    fields = '__all__'
    redirect_authenticated_user = True #That means if a user acc is already created this will wont appear to him then

    def get_success_url(self):
        return reverse_lazy('tasks')
    

    
class TaskList(LoginRequiredMixin, ListView): #So we use this mixin with all task views kionke agar hum iske bagair task-1/ par jaenge to hum bagair login ke access karsakte usko isliye humne yeh mixin use kia hai.
    model = Task
    context_object_name = 'tasks'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tasks'] = context['tasks'].filter(user=self.request.user)
        context['count'] = context['tasks'].filter(complete=False).count()
    
        search_input = self.request.GET.get('search-area') or ''
        if search_input:
            context['tasks'] = context['tasks'].filter(
                title__startswith=search_input)           #this means ke agar search-input jo ke eik search box hai agar us word ke 1st letter given task se match hogae to to usko search-input variable me pass kardena jo ke reload honey par task display kardega kionke wo task ke pehle letter se filter kardega
            
        context['search_input'] = search_input 
        return context  #This means ke search_input context me pass kardia hai or yeh hume foran foran bagair page load huey task nikal ke dega
        
class RegisterPage(FormView):
    template_name = 'base/register.html'
    form_class = UserCreationForm
    redirect_authenticated_user = True
    success_url = reverse_lazy('tasks')

    def form_valid(self, form): #So we used this method to redirect the user once he registered his acc
        user = form.save()
        if user is not None:
            login(self.request, user) #If its register form is valid the login him as user
        return super(RegisterPage, self).form_valid(form)

    def get(self, *args, **kwargs): #So we used this method so that authenticated user can't access to register and login page
        if self.request.user.is_authenticated:
            return redirect('tasks')
        return super(RegisterPage, self).get(*args, **kwargs)

class TaskDetail(LoginRequiredMixin, DetailView):
    model = Task  
    context_object_name = 'task'
    template_name = 'base/task.html'   

class TaskCreate(LoginRequiredMixin, CreateView):
    model = Task
    fields = ['title', 'description', 'complete']
    success_url = reverse_lazy('tasks')

    def form_valid(self, form):  #We used this method so that each user can create their items from their own user account.
        form.instance.user = self.request.user
        return super(TaskCreate, self).form_valid(form)
    

class TaskUpdate(LoginRequiredMixin, UpdateView):
    model = Task
    fields = ['title', 'description', 'complete']
    success_url = reverse_lazy('tasks')

class DeleteView(LoginRequiredMixin, DeleteView):
    model = Task
    context_object_name = 'task'
    success_url = reverse_lazy('tasks')


class TaskReorder(View):
    def post(self, request):
        form = PositionForm(request.POST)

        if form.is_valid():
            positionList = form.cleaned_data["position"].split(',')

            with transaction.atomic():
                self.request.user.set_task_order(positionList)

        return redirect(reverse_lazy('tasks'))