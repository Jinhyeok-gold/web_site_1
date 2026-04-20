from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import json
from .services import ask_expert_ai, generate_expert_report
from .models import UserProfile as ChatbotProfile
from auth_mypage.models import UserProfile as PolicyProfile
from youth_road.models import UserDiagnostic, HousingProduct, FinanceProduct, WelfareProduct
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
                is_pregnant=u.get('is_pregnant', False),
                subscription_count=u.get('sub_count', 24),
                subscription_amount=u.get('sub_amount', 240),
                is_homeless=u.get('is_homeless', True),
                is_first_home=u.get('first_home', True),
                homeless_years=u.get('homeless_years', 0)
            )
            
            # [STRICT] 매칭 엔진 가동
            report = MatchingEngine.get_full_report(diag)
            
            # [SAVE] 로그인 상태라면 진단 데이터를 DB에 영구 보관
            if request.user.is_authenticated:
                diag.user = request.user
                diag.save()
                u['diagnostic_id'] = diag.id 

                # [SYNC] auth_mypage의 UserProfile 동기화 (사이드바 및 전역 연동용)
                p_prof, _ = PolicyProfile.objects.get_or_create(user=request.user)
                p_prof.age = diag.age
                p_prof.income = diag.total_income
                p_prof.net_assets = diag.assets
                p_prof.debt = diag.debt
                p_prof.sido = MatchingEngine.get_hangeul_region(diag.region)
                p_prof.sigungu = diag.sub_region
                p_prof.subscription_count = diag.subscription_count
                p_prof.subscription_amount = diag.subscription_amount
                p_prof.marital_status = "신혼부부" if diag.marital_status == "Married" else "미혼"
                p_prof.children_count = diag.kids_count
                p_prof.is_pregnant = diag.is_pregnant
                p_prof.is_first_home = diag.is_first_home
                p_prof.is_homeless = diag.is_homeless
                p_prof.save()

                # [SYNC] chatbot.core의 UserProfile 동기화 (AI 비서용)
                c_prof, _ = ChatbotProfile.objects.get_or_create(user=request.user)
                c_prof.age = diag.age
                c_prof.income = diag.total_income
                c_prof.region = diag.region
                c_prof.sub_region = diag.sub_region
                c_prof.save()
            
            # 세션에 최신 진단 데이터 캐싱 (AI 리포트 호출 시 사용)
            request.session['latest_diagnostic_data'] = u
            request.session['latest_report_data'] = report
            request.session.modified = True
            
            return JsonResponse({'report': report})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request'}, status=400)

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

@login_required
def send_user_report_email(request):
    """현재 로그인된 사용자에게 정밀 분석 보고서 이메일 발송 (DB 폴백 탑재)"""
    if request.method == 'POST':
        try:
            # 1. 세션에서 데이터 우선 확인
            user_data = request.session.get('latest_diagnostic_data')
            report_data = request.session.get('latest_report_data')
            
            # 2. [v22] 세션에 없으면 DB에서 최신 진단 결과 조회 (폴백)
            if not user_data or not report_data:
                latest_diag = UserDiagnostic.objects.filter(user=request.user).order_by('-created_at').first()
                if latest_diag:
                    # 매칭 엔진을 다시 가동하여 리포트 생성
                    report_data = MatchingEngine.get_full_report(latest_diag)
                    user_data = {
                        'age': latest_diag.age,
                        'region': latest_diag.region,
                        'income': latest_diag.total_income,
                        # 필요한 다른 필드들도 여기에 추가 가능
                    }
                else:
                    return JsonResponse({'error': '저장된 진단 데이터가 없습니다. 먼저 자가진단을 진행해 주세요.'}, status=400)
            
            user_email = request.user.email
            if not user_email:
                return JsonResponse({'error': '계정에 등록된 이메일 주소가 없습니다. [회원정보 수정]에서 이메일을 등록해 주세요.'}, status=400)

            # HTML 이메일 템플릿 렌더링
            context = {
                'user': request.user,
                'data': user_data,
                'report': report_data,
            }
            
            subject = f"[딱맞춤] {request.user.last_name or request.user.username}님의 정밀 분석 보고서입니다."
            html_message = render_to_string('chatbot/email_report.html', context)
            plain_message = strip_tags(html_message)
            
            from django.conf import settings
            send_mail(
                subject,
                plain_message,
                settings.DEFAULT_FROM_EMAIL,
                [user_email],
                html_message=html_message,
                fail_silently=False  # 오류 발생 시 예외 발생 (디버깅용)
            )
            
            return JsonResponse({'status': 'success', 'message': f'{user_email}로 리포트가 전송되었습니다. (진단 데이터: {"공급원 - 세션" if request.session.get("latest_diagnostic_data") else "공급원 - DB"})'})
        except Exception as e:
            import traceback
            print(traceback.format_exc()) # 서버 로그에 상세 오류 출력
            return JsonResponse({'error': f'메일 발송 중 오류가 발생했습니다: {str(e)}'}, status=500)
    return JsonResponse({'error': '잘못된 요청 방식입니다.'}, status=400)

@csrf_exempt
def chat_gemini(request):
    """전문가 AI 채팅 API (v21 Contextual)"""
    if request.method == 'POST':
        try:
            body = json.loads(request.body)
            user_msg = body.get('message', '')
            
            # 자가진단(body의 user_data) 우선 연동
            frontend_user_data = body.get('user_data')
            if frontend_user_data:
                user_data = frontend_user_data
            else:
                user_data = request.session.get('latest_diagnostic_data', {'name': '방문자', 'age': 29, 'income': 3000, 'region': 'Seoul'})
                
            report_data = body.get('report_data') or request.session.get('latest_report_data', None)
            
            user_api_key = None
            if request.user.is_authenticated:
                try:
                    p = getattr(request.user, 'userprofile', None)
                    if p:
                        user_api_key = p.personal_api_key
                except Exception:
                    pass

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
        # [v22] 프로필 존재 여부 확인 (없으면 생성)
        if not hasattr(request.user, 'userprofile'):
            ChatbotProfile.objects.create(user=request.user, name=request.user.username)
        
        profile = request.user.userprofile
        profile.name = request.POST.get('name', profile.name)
        profile.age = int(request.POST.get('age', profile.age or 29))
        profile.income = int(request.POST.get('income', profile.income or 3000))
        profile.region = request.POST.get('region', profile.region or 'Seoul')
        profile.sub_region = request.POST.get('sub_region', profile.sub_region)
        profile.personal_api_key = request.POST.get('personal_api_key', profile.personal_api_key)
        profile.save()
        return redirect('home') # home으로 변경 (mainwindow)
    return redirect('home')

@csrf_exempt
def get_product_detail(request):
    """[v22] 특정 상품의 상세 정보를 반환 (AI 카드 렌더링용)"""
    product_id = request.GET.get('id')
    if not product_id:
        return JsonResponse({'error': 'No ID provided'}, status=400)
    
    # 여러 테이블에서 ID 검색
    product = None
    if product_id.startswith('HOU_'):
        product = HousingProduct.objects.filter(manage_no=product_id.replace('HOU_', '')).first()
    elif product_id.startswith('FIN_'):
        product = FinanceProduct.objects.filter(product_id=product_id).first()
    elif product_id.startswith('WEL_'):
        product = WelfareProduct.objects.filter(policy_id=product_id).first()
    else:
        # [Fallback] 접두어 없이 들어온 경우 전체 테이블 검색
        product = HousingProduct.objects.filter(manage_no=product_id).first() or \
                  FinanceProduct.objects.filter(product_id=product_id).first() or \
                  WelfareProduct.objects.filter(policy_id=product_id).first()
    
    if product:
        return JsonResponse({
            'id': product_id,
            'title': product.title,
            'summary': getattr(product, 'benefit_desc', getattr(product, 'location', '상세 정보 없음')),
            'url': getattr(product, 'url', '#'),
            'type': product.__class__.__name__
        })
    
    return JsonResponse({'error': 'Product not found'}, status=404)
