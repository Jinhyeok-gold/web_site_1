from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .services import get_all_policies, ask_expert_ai, generate_expert_report
from .models import UserProfile

@csrf_exempt
def match_policies(request):
    """전체 정책 매칭 API (POST로 사용자 진단 데이터 수락 가능)"""
    user_data = {}
    
    # 1. 로그인된 유저 프로필 우선
    if request.user.is_authenticated:
        try:
            profile, _ = UserProfile.objects.get_or_create(user=request.user)
            user_data = {'age': profile.age, 'income': profile.income, 'region': profile.region, 'marital': 'single'}
        except: pass

    # 2. POST로 넘어온 진단 데이터가 있다면 덮어쓰기
    if request.method == 'POST':
        try:
            body = json.loads(request.body)
            # data가 null이거나 없을 경우를 대비해 처리
            provided_data = body.get('user_data')
            if provided_data and isinstance(provided_data, dict):
                user_data.update(provided_data)
        except: pass
    
    try:
        policies = get_all_policies(user_data)
        return JsonResponse({'policies': policies})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def chat_gemini(request):
    """전문가 AI 채팅 API"""
    if request.method == 'POST':
        try:
            body = json.loads(request.body)
            user_msg = body.get('message', '')
            # user_data가 null로 오면 기본값으로 대체
            user_data = body.get('user_data')
            if not user_data or not isinstance(user_data, dict):
                user_data = {'name': '방문자', 'age': 29, 'income': 3000, 'region': 'seoul', 'marital': 'single'}
            
            if request.user.is_authenticated:
                try:
                    p, _ = UserProfile.objects.get_or_create(user=request.user)
                    user_data.update({
                        'name': p.name or request.user.username,
                        'age': p.age,
                        'income': p.income,
                        'region': p.region
                    })
                except: pass
            
            # 컨텍스트 보강
            try:
                user_data['top_matches'] = get_all_policies(user_data)[:5]
            except:
                user_data['top_matches'] = []
            
            reply = ask_expert_ai(user_msg, user_data)
            return JsonResponse({'reply': reply})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def get_ai_report(request):
    """정밀 진단 AI 보고서 API"""
    if request.method == 'POST':
        try:
            body = json.loads(request.body)
            # user_data가 null로 오면 기본값으로 대체
            user_data = body.get('user_data')
            if not user_data or not isinstance(user_data, dict):
                user_data = {'name': '사용자', 'age': 29, 'income': 3000, 'region': 'seoul', 'marital': 'single'}
                
            top_matches = body.get('top_matches')
            if not top_matches:
                top_matches = get_all_policies(user_data)[:5]
            
            report = generate_expert_report(user_data, top_matches)
            return JsonResponse({'report': report})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request'}, status=400)
