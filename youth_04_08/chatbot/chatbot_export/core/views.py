from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import json
from .services import get_all_policies, ask_expert_ai, generate_expert_report
from .models import UserProfile

def index(request):
    """SPA Main Entry Point"""
    return render(request, 'index.html')

def match_policies(request):
    """전체 정책 매칭 API"""
    user_data = {}
    if request.user.is_authenticated:
        profile = request.user.userprofile
        user_data = {'age': profile.age, 'income': profile.income, 'region': profile.region}
    
    policies = get_all_policies(user_data)
    return JsonResponse({'policies': policies})

@csrf_exempt
def chat_gemini(request):
    """전문가 AI 채팅 API"""
    if request.method == 'POST':
        try:
            body = json.loads(request.body)
            user_msg = body.get('message', '')
            user_data = {'name': '방문자', 'age': 29, 'income': 3000, 'region': 'seoul'}
            
            if request.user.is_authenticated:
                p = request.user.userprofile
                user_data = {
                    'name': p.name or request.user.username,
                    'age': p.age,
                    'income': p.income,
                    'region': p.region
                }
            
            # 컨텍스트 보강 (에러 방지를 위해 예외 처리)
            try:
                user_data['top_matches'] = get_all_policies(user_data)[:5]
            except:
                user_data['top_matches'] = []
            
            reply = ask_expert_ai(user_msg, user_data)
            return JsonResponse({'reply': reply})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
@csrf_exempt
def get_ai_report(request):
    """정밀 진단 AI 보고서 API"""
    if request.method == 'POST':
        try:
            body = json.loads(request.body)
            top_matches = body.get('top_matches', [])
            p = request.user.userprofile
            user_data = {
                'name': p.name or request.user.username,
                'age': p.age,
                'income': p.income,
                'region': p.region
            }
            
            report = generate_expert_report(user_data, top_matches)
            return JsonResponse({'report': report})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def update_profile(request):
    """사용자 프로필 실시간 업데이트"""
    if request.method == 'POST':
        profile = request.user.userprofile
        profile.name = request.POST.get('name', profile.name)
        profile.age = int(request.POST.get('age', profile.age))
        profile.income = int(request.POST.get('income', profile.income))
        profile.save()
        return redirect('index')
    return redirect('index')
