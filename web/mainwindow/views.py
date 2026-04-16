from django.shortcuts import render
from youth_road.models import WelfareProduct, HousingProduct, UserDiagnostic
from django.db.models import Q
from django.contrib.auth.decorators import login_required

def home(request):
    context = {
        'title': '홈페이지',
    }
    return render(request, 'mainwindow/home.html', context)

@login_required
def myreport(request):
    return render(request, 'mainwindow/myreport.html')

def welfare_map(request):
    return render(request, 'mainwindow/welfare_map.html')
