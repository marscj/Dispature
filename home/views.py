from django.shortcuts import render
from django.http import HttpResponse

def home(request):
    context          = {}
    context['hello'] = '网站正在制作中!'
    return render(request, 'home.html', context)
