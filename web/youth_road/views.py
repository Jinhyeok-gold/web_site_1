from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from .forms import DiagnosticForm
from .models import UserDiagnostic
from .matching_service import MatchingEngine

def index(request):
    return redirect('home')

def diagnose(request):
    """Redirect to main hub for diagnosis"""
    return redirect('home')

def result(request, pk):
    """Redirect to main hub (result should be handled in-page or via main report)"""
    return redirect('home')

# 인증 및 회원 관리 (Redirect to portal)
def signup(request):
    return redirect('policy:register_step1')

def login_view(request):
    return redirect('policy:login')

def logout_view(request):
    return redirect('policy:logout')

@login_required
def my_reports(request):
    """Redirect to consolidated report view"""
    return redirect('myreport')

