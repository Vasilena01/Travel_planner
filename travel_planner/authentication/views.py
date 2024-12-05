from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages

def register_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        if password == confirm_password:
            try:
                User.objects.create_user(
                    username=username, email=email, password=password)
                messages.success(request, 'Account created successfully')
                return redirect('login')
            except:
                messages.error(request, 'Error creating account')
        else:
            messages.error(request, 'Passwords do not match')
    return render(request, 'authentication/register.html')


def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('homepage')
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'authentication/login.html')


def logout_user(request):
    logout(request)
    return redirect('homepage')