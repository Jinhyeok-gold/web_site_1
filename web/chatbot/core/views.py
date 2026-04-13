from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import json
from .services import get_all_policies, ask_expert_ai, generate_expert_report
from .models import UserProfile
from youth_road.models import UserDiagnostic
from youth_road.matching_service import MatchingEngine

def index(request):
    """SPA Main Entry Point"""
    return render(request, 'chatbot/index.html')

def match_policies(request):
    """전체 정책 매치 API (v21 Hyper-Precision)"""
    if request.method == 'POST':
        try:
            body = json.loads(request.body)
            u = body.get('user_data', {})
            
            # [v21] UserDiagnostic 인스턴스 생성 (DB 저장 없이 메모리 상 분석용)
            # 로그인이 되어있다면 나중에 저장하거나 프로필 연동 가능
            diag = UserDiagnostic(
                age=u.get('age', 29),
                region=u.get('region', 'Seoul'),
                sub_region=u.get('sub_region', ''),
                marital_status=u.get('marital', 'Single'),
                total_income=u.get('income', 3000),
                assets=u.get('assets', 5000),
                debt=u.get('debt', 0),
                kids_count=u.get('kids', 0),
                subscription_count=u.get('sub_count', 24),
                is_homeless=u.get('is_homeless', True),
                is_first_home=u.get('first_home', True),
                homeless_years=5 # 기본값
            )
            
            # [STRICT] 매칭 엔진 가동
            report = MatchingEngine.get_full_report(diag)
            
            # 세션에 최신 진단 데이터 캐싱 (AI 리포트 호출 시 사용)
            request.session['latest_diagnostic_data'] = u
            request.session['latest_report_data'] = report
            request.session.modified = True
            
            return JsonResponse({'report': report})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def chat_gemini(request):
    """전문가 AI 채팅 API (v21 Contextual)"""
    if request.method == 'POST':
        try:
            body = json.loads(request.body)
            user_msg = body.get('message', '')
            user_data = request.session.get('latest_diagnostic_data', {'name': '방문자', 'age': 29, 'income': 3000, 'region': 'Seoul'})
            report_data = request.session.get('latest_report_data', None)
            
            user_api_key = None
            if request.user.is_authenticated:
                p = request.user.userprofile
                user_api_key = p.personal_api_key

            chat_history = request.session.get('chat_history', [])
            reply = ask_expert_ai(user_msg, user_data, report_data, user_api_key=user_api_key, history=chat_history)
            
            chat_history.append({"role": "user", "parts": [{"text": user_msg}]})
            chat_history.append({"role": "model", "parts": [{"text": reply}]})
            request.session['chat_history'] = chat_history[-10:]
            request.session.modified = True

            return JsonResponse({'reply': reply})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def get_ai_report(request):
    """정밀 진단 AI 보고서 생성 API (v21 Personalized)"""
    if request.method == 'POST':
        try:
            body = json.loads(request.body)
            u = body.get('user_data', {})
            report_data = body.get('report_data', {})
            
            # 🎯 AI에게 넘길 컨텍스트 구성
            user_data_prompt = {
                'name': request.user.username if request.user.is_authenticated else '방문자',
                'age': u.get('age'),
                'income': u.get('income'),
                'region': u.get('region'),
                'assets': u.get('assets'),
                'debt': u.get('debt'),
                'marital': u.get('marital')
            }
            
            top_matches = []
            if report_data:
                for cat in ['housing', 'finance', 'welfare']:
                    if report_data.get(cat) and report_data[cat].get('top_1'):
                        top_matches.append(report_data[cat]['top_1'])

            report = generate_expert_report(user_data_prompt, top_matches)
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
        profile.region = request.POST.get('region', profile.region)
        profile.sub_region = request.POST.get('sub_region', profile.sub_region)
        profile.personal_api_key = request.POST.get('personal_api_key', profile.personal_api_key)
        profile.save()
        return redirect('index')
    return redirect('index')
