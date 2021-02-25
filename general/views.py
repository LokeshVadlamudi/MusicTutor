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



# Create your views here.

@login_required(login_url='login')
def home(request):
    return render(request, 'home.html')


@csrf_exempt
def predict_song(request):
    if request.method == 'POST':
        context = ['Classical', 'Hipop', 'Jazz', 'Metal', 'Pop', 'Rock']
        print(request.body)
        headers = {'content-type': 'audio/wav'}
        files = {'file': request.body}
        data = request.body

        url = "http://ec2-54-82-81-212.compute-1.amazonaws.com:8000/songPred"
        try:
            # r = requests.post(url, files = files)
            r = requests.post(url, data=data, headers=headers)
            print("request sending", r)
        except:
            print("error sending request")
        # print("JSONdata['file']: ", JSONdata)

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

            user = authenticate(request, username = username, password = password)
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
