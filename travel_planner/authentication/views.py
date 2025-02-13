from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import UserRegistrationForm
from .forms import UserLoginForm

def register_user(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, 'Account created successfully. Please login.')
            return redirect('login')
        # else:
        #     return render(request, 'authentication/register.html', {'form': form})
    else:
        form = UserRegistrationForm()

    return render(request, 'authentication/register.html', {'form': form})

def login_user(request):
    form = UserLoginForm()
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('homepage')
        else:
            messages.error(request, 'Invalid username or password')

    return render(request, 'authentication/login.html', {'form': form})

def logout_user(request):
    logout(request)
    return redirect('homepage')