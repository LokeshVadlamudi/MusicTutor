from django.shortcuts import render
# encoding: utf-8
import json
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import CreateView, DeleteView, ListView, DetailView
from django.views.decorators.csrf import csrf_exempt
import requests
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from .forms import CreateUserForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout

# s3 upload
import boto3
from botocore.exceptions import NoCredentialsError
import tinys3


# Create your views here.

@login_required(login_url='login')
def home(request):
    return render(request, 'home.html')


@csrf_exempt
def predict_song(request):
    if request.method == 'POST':

        ACCESS_KEY = 'AKIAUNLOXSXREJISSC6D'
        SECRET_KEY = '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'

        username = request.user.username
        # fileName = request.FILES['mySong'].name

        with open('myfile.mp3', mode='wb') as f:
            f.write(request.body)

        f = open('myfile.mp3', mode='rb')

        fileName = request.FILES['mySong'].name

        conn = tinys3.Connection(ACCESS_KEY, SECRET_KEY, tls=True)
        conn.upload(username + '/' + fileName, f, 'musictutor')

        return HttpResponse("success")

    if request.method == 'GET':
        return HttpResponse('nothing here')


# user management

# user login
@csrf_exempt
def loginPage(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                messages.info(request, 'username or password is incorrect')

        context = {

        }
        return render(request, 'login.html', context)


# register user
@csrf_exempt
def registerPage(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        form = CreateUserForm()

        if request.method == 'POST':
            form = CreateUserForm(request.POST)
            if form.is_valid():
                form.save()
                user = form.cleaned_data.get('username')
                messages.success(request, 'Account was created for :' + user)
                return redirect('login')
        context = {
            'form': form
        }
        return render(request, 'register.html', context)


# user logout
@csrf_exempt
def logoutUser(request):
    logout(request)
    return redirect('login')
