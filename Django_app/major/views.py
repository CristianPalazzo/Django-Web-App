from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse
from django.contrib.auth import login,logout,authenticate
from django.contrib.auth.models import User
from django.db import IntegrityError
from .forms import TaskForm
from .models import Task
from django.utils import timezone
from django.contrib.auth.decorators import login_required


# Create your views here.
def home(request):
    nameuser= request.user
    body_class='home'
    return render(request,'home.html',{'nameuser':nameuser,'body_class':body_class})

def signup(request):
    body_class='signup'
    if request.method == 'GET':
        return render(request,'logi.html',{'body_class':body_class})
    else:
        if request.POST['password1'] == request.POST['password2']:
            print(request.POST)
            try:
                user = User.objects.create_user(username=request.POST['name'],
                                                password=request.POST['password1'])
                user.save()
                login(request,user)

                return redirect('tasks')
            except IntegrityError:
                return render(request,'logi.html',{"error":'User already exists','body_class':body_class}) 
        else:
            return HttpResponse("Las contraseñas no coinciden")   
        
def signin(request):
    body_class='signin'
    if request.method == 'GET':
        return render(request,'signin.html',{'body_class':body_class})
    else:
        user = authenticate(request, username=request.POST['name'],password=request.POST['password'])

        if user is None:
            return render(request,'signin.html',
                          {'error':'Username or password is incorrect',
                           'body_class':body_class})
        else:
            login(request,user)
            return redirect('tasks')

@login_required
def logo(request):
    logout(request)
    return redirect('home')

@login_required
def tasks(request):
    body_class='tasks'
    nameuser= request.user
    tasks = Task.objects.filter(user=request.user,datecompleted__isnull=True)
    status='Pending'
    return render(request,'tasks.html',{'tasks':tasks,'status':status,'nameuser':nameuser,'body_class':body_class})        

@login_required
def tasks_completed(request):
    body_class='tasks_completed'
    nameuser= request.user
    tasks = Task.objects.filter(user=request.user,datecompleted__isnull=False).order_by
    ('-datecompleted')
    status='Completed'
    return render(request,'tasks.html',{'tasks':tasks,'status':status,'nameuser':nameuser,'body_class':body_class}) 

@login_required
def create_task(request):
    body_class='tasks_create'
    nameuser= request.user
    if request.method =='GET':
        return render(request,'create_task.html',{
            'form': TaskForm,
            'nameuser':nameuser,
            'body_class':body_class
        })     
    else:
        try:
            form = TaskForm(request.POST)
            new_task = form.save(commit=False)
            new_task.user = request.user
            new_task.save()
            return redirect('tasks')   
        except ValueError:
            return render(request,'create_task.html',{
            'form': TaskForm,
            'nameuser':nameuser,
            'error':'Invalid data or User has not logged in',
            'body_class':body_class
            })

@login_required
def task_detail(request, task_id):
    body_class='task_detail'
    nameuser= request.user
    if request.method == 'GET':
        task = get_object_or_404(Task, pk=task_id, user=request.user)
        form = TaskForm(instance=task)
        return render(request,'task_detail.html',{'task':task, 'form':form,'body_class':body_class,'nameuser':nameuser})
    else:
        try:
            task = get_object_or_404(Task, pk=task_id, user=request.user)
            form = TaskForm(request.POST, instance=task)
            form.save()
            return redirect('tasks')
        except ValueError:
            return render(request,'task_detail.html',{'task':task, 'form':form,
                                                      'error':"Error updating task",
                                                      'body_class':body_class,
                                                      'nameuser':nameuser})

@login_required
def complete_task(request,task_id):
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    if request.method == 'POST':
        task.datecompleted = timezone.now()
        task.save()
        return redirect('tasks')

@login_required
def delete_task(request,task_id):
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    if request.method == 'POST':
        task.delete()
        return redirect('tasks')
