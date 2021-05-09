from django.shortcuts import render


# Create your views here.
@login_required(login_url='login')
def index(request):
    return render(request, 'index.html', {})

@login_required(login_url='login')
def room(request, room_name):
    return render(request, 'chatroom.html', {'room_name': room_name})
