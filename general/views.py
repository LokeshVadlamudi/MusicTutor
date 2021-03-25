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
import keras, cv2
import d6tpipe
import boto3
import os

# pylab
import os
import wave
import pylab

# conversion wav to png

import librosa
import pandas as pd
import numpy as np
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
from PIL import Image
import pathlib
import csv


# Create your views here.

@login_required(login_url='login')
def home(request):
    username = request.user.username
    context = {
        'username': username
    }
    return render(request, 'home.html', context)


@login_required(login_url='login')
def uploads(request):
    username = request.user.username

    # print('inside uploads view')

    access_key = 'AKIAUNLOXSXREJISSC6D'
    secret_key = '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'

    s3 = boto3.resource('s3', aws_access_key_id=access_key, aws_secret_access_key=secret_key)
    bucket = s3.Bucket('musictutor')
    # Iterates through all the objects, doing the pagination for you. Each obj
    # is an ObjectSummary, so it doesn't contain the body. You'll need to call
    # get to get the whole body.
    objs = bucket.objects.filter(Prefix=username)

    songList = []
    for obj in objs:
        key = obj.key
        songName = key.split('/')[1]
        songList.append((songName, 'https://musictutor.s3.amazonaws.com' + '/' + key))

    context = {
        'songList': songList,
        'username': username
    }

    return render(request, 'uploads.html', context)


@csrf_exempt
def predict_song(request):
    if request.method == 'POST':
        ACCESS_KEY = 'AKIAUNLOXSXREJISSC6D'
        SECRET_KEY = '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'

        username = request.user.username
        # fileName = request.FILES['mySong'].name

        songname = 'mysong.mp3'
        with open(songname, mode='wb') as f:
            f.write(request.body)

        f = open(songname, mode='rb')
        fileName = request.FILES['mySong'].name

        conn = tinys3.Connection(ACCESS_KEY, SECRET_KEY, tls=True)
        conn.upload(username + '/' + fileName, f, 'musictutor')

        # converting to png file
        cmap = plt.get_cmap('inferno')
        y, sr = librosa.load(songname, mono=True)
        plt.specgram(y, NFFT=2048, Fs=2, Fc=0, noverlap=128, cmap=cmap, sides='default', mode='default', scale='dB');
        plt.axis('off')
        plt.savefig('myfile.png')
        plt.clf()
        classifier = keras.models.load_model("cool.h5")
        img = cv2.imread("myfile.png")
        img = cv2.resize(img, (150, 150))  # resize the image
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        image = np.expand_dims(img, axis=0)
        classifier.predict_classes(image)
        print(classifier.predict_classes(image))
        print('class is ' + str(classifier.predict_classes(image)[0]))

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
