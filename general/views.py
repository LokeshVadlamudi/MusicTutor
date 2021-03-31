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
import os

# pylab
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
@csrf_exempt
def home(request):

    username = request.user.username

    # uploads

    access_key = 'AKIAUNLOXSXREJISSC6D'
    secret_key = 'r6HL8lS/SxIdNinI8MHutOAsbMY5oojyMmugL9Kg'

    s3 = boto3.resource('s3', aws_access_key_id=access_key, aws_secret_access_key=secret_key)
    bucket = s3.Bucket('musictutor')
    # Iterates through all the objects, doing the pagination for you. Each obj
    # is an ObjectSummary, so it doesn't contain the body. You'll need to call
    # get to get the whole body.
    objs = bucket.objects.filter(Prefix=username)

    songList = []

    try:
        for obj in objs:
            key = obj.key
            songName = key.split('/')[1]
            songList.append((songName, 'https://musictutor.s3.amazonaws.com' + '/' + key))
    except:
        songList = []

    context = {
        'songList': songList,
        'username': username,
        'raga' : None,
    }

    #predict song

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

        # sending s3 link to prediction microservice.
        s3link = 'https://musictutor.s3.amazonaws.com/' + username + '/' + fileName

        print(s3link)

        def predict_raga(fp):
            y, sr = librosa.load(fp, res_type='kaiser_best')
            mfcc = librosa.feature.mfcc(y=y, sr=22050, hop_length=512, n_mfcc=13)
            mfcc = mfcc.T

            data = {
                "mfcc": []
            }

            data["mfcc"].append(mfcc.tolist())

            X = np.array(data["mfcc"])

            data = json.dumps({"signature_name": "serving_default", "instances": X.tolist()})
            print('Data: {} ... {}'.format(data[:50], data[len(data) - 52:]))

            headers = {"content-type": "application/json"}
            json_response = requests.post('http://34.72.124.124:8501/v1/models/classify_raga:predict', data=data,
                                          headers=headers)

            predictions = json.loads(json_response.text)['predictions']
            class_names = ['De╠äs╠ü',
                           'Bhairavi',
                           'Bila╠äsakha╠äni╠ä to╠äd╠úi╠ä',
                           'Ba╠äge╠äs╠üri╠ä',
                           'Ahira bhairav']


            return (class_names[np.argmax(predictions)])
        raga = predict_raga('mysong.mp3')

        print(raga)

        context["raga"] = raga

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

        # sending s3 link to prediction microservice.
        s3link = 'https://musictutor.s3.amazonaws.com/' + username + '/' + fileName

        print(s3link)

        def predict_raga(fp):
            y, sr = librosa.load(fp, res_type='kaiser_best')
            mfcc = librosa.feature.mfcc(y=y, sr=22050, hop_length=512, n_mfcc=13)
            mfcc = mfcc.T

            data = {
                "mfcc": []
            }

            data["mfcc"].append(mfcc.tolist())

            X = np.array(data["mfcc"])

            data = json.dumps({"signature_name": "serving_default", "instances": X.tolist()})
            print('Data: {} ... {}'.format(data[:50], data[len(data) - 52:]))

            headers = {"content-type": "application/json"}
            json_response = requests.post('http://34.72.124.124:8501/v1/models/classify_raga:predict', data=data,
                                          headers=headers)

            predictions = json.loads(json_response.text)['predictions']
            class_names = ['De╠äs╠ü',
                           'Bhairavi',
                           'Bila╠äsakha╠äni╠ä to╠äd╠úi╠ä',
                           'Ba╠äge╠äs╠üri╠ä',
                           'Ahira bhairav']


            return (class_names[np.argmax(predictions)])
        raga = predict_raga('mysong.mp3')

        print(raga)

        content = {
            "raga": raga
        }

        return redirect('/', content)

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
