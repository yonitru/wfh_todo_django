from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth import login, logout, authenticate
from .forms import TodoForm
from .models import Todo
from django.utils import timezone
from django.contrib.auth.decorators import login_required

def registerform(request):
    if request.method == 'GET':
        return render(request, 'todo/registerform.html', {'form':UserCreationForm()})
    else:
        #create a new user: LOGIC- CAN BE IN CONTROLLER
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(request.POST['username'],password=request.POST['password1'])
                user.save()
                login(request, user)
                return redirect('mytodos')
            
            except IntegrityError:
                return render(request, 'todo/registerform.html', {'form':UserCreationForm(), 'errMsg':'User exists. Choose a different one'})
              
        else:
            return render(request, 'todo/registerform.html', {'form':UserCreationForm(), 'errMsg':'Password did not match'})


@login_required
def mytodos(request):
    todos = Todo.objects.filter(user_id=request.user,dateCompleted__isnull=True).order_by('-dateCreated')
    return render(request, 'todo/mytodos.html',{'alltodos':todos})

def loginuser(request):
    if request.method == 'GET':
        return render(request, 'todo/loginform.html', {'form':AuthenticationForm()})
    else:
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'todo/loginform.html', {'form':AuthenticationForm(), 'errMsg':'user does not exist'})
        else:
            login(request, user)
            return redirect('mytodos')

@login_required
def logoutuser(request):
    if request.method == 'POST':
        logout(request)
        return redirect('homepage')

def homepage(request):
    return render(request, 'todo/index.html')

@login_required
def createNewTodo(request):
    if request.method == 'GET':
        return render(request, 'todo/createnewtodo.html', {'form':TodoForm()})
    else:
        try:
            form = TodoForm(request.POST)
            newtodo = form.save(commit=False)
            newtodo.user_id = request.user
            newtodo.save()
            return redirect('mytodos')
        except ValueError:
            return render(request, 'todo/createnewtodo.html', {'form':TodoForm(), 'errMsg':'Data mismatch'})

@login_required
def updatetodo(request,todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user_id=request.user)

    if request.method == 'GET':
        form = TodoForm(instance=todo)
        return render(request, 'todo/updatetodo.html',{'todo':todo,'form':form}) 
    else:
        try:
            form = TodoForm(request.POST, instance=todo)
            form.save()
            return redirect('mytodos')
        except ValueError:
            return render(request, 'todo/updatetodo.html', {'form':TodoForm(), 'errMsg':'Data mismatch'})

@login_required
def donetodo(request,todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user_id=request.user)
    if request.method == 'POST':
        todo.dateCompleted = timezone.now()
        todo.save()
        return redirect('mytodos')

@login_required
def deletetodo(request,todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user_id=request.user)
    if request.method == 'POST':
        todo.delete()
        return redirect('mytodos')