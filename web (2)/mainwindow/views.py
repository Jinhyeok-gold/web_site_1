from django.shortcuts import render
from youth_road.models import WelfareProduct, HousingProduct, UserDiagnostic
from django.db.models import Q

def home(request):
    context = {
        'title': '홈페이지',
    }
    return render(request, 'mainwindow/home.html', context)

def myreport(request):
    return render(request, 'mainwindow/myreport.html')

def welfare_map(request):
    return render(request, 'mainwindow/welfare_map.html')
