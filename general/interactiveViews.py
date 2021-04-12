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


@login_required(login_url='login')
@csrf_exempt
def selectRaga(request):
    username = request.user.username


    if request.method == 'POST':
        ragaType = request.POST.get('raga')
        print(ragaType)

        context = {
            'ragaType' : ragaType
        }
        return render(request,'uploadMethod.html', context)

    context = {

    }
    return render(request, 'selectRaga.html', context)


@login_required(login_url='login')
@csrf_exempt
def uploadRaga(request):
    username = request.user.username

    if request.method == 'POST':
        # ragaType = request.POST.get('raga')
        # print(ragaType)
        # audio_data = request.FILES.get('data')
        # path = default_storage.save('123' + '.mp3', ContentFile(audio_data.read()))

        ACCESS_KEY = 'AKIA4BFL45UA4BYQ7XLP'

        SECRET_KEY = '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'

        context = {}

        songname = 'mysong.mp3'

        with open(songname, mode='wb') as f:
            f.write(request.body)

        f = open(songname, mode='rb')

        try:
            fileName = request.FILES['mySong'].name
        except:
            context = {
                'error' : 'Select the audio file'
            }
            return render(request, 'uploadMethod.html', context)

        conn = tinys3.Connection(ACCESS_KEY, SECRET_KEY, tls=True)
        conn.upload(username + '/' + fileName, f, 'musictutor-storage')

        # sending s3 link to prediction microservice.
        s3link = 'https://musictutor-storage.s3.amazonaws.com/' + username + '/' + fileName

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
            json_response = requests.post('http://35.188.146.134:8501/v1/models/classify_raga:predict', data=data,
                                          headers=headers)

            predictions = json.loads(json_response.text)['predictions']
            class_names = ['De╠äs╠ü',
                           'Bhairavi',
                           'Bila╠äsakha╠äni╠ä to╠äd╠úi╠ä',
                           'Ba╠äge╠äs╠üri╠ä',
                           'Ahira bhairav']

            print(predictions)
            return (class_names[np.argmax(predictions)])

        
        # raga = predict_raga('mysong.mp3')

        raga = 'Bhairavi'

        print(raga)

        context["raga"] = raga
        
        return render(request,'result.html', context)

    context = {

    }
    return render(request, 'selectRaga.html', context)











