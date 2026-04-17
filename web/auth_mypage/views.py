from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from .models import UserProfile

# --- [보안 패치] 입력데이터 검증용 상수 및 함수 ---
VALID_MARITAL_STATUSES = ["미혼", "결혼예정", "신혼부부", "기혼"]

def to_pos_int(val, default=0):
    """입력값을 양의 정수로 안전하게 변환 (음수는 0으로 처리)"""
    try:
        if val is None or str(val).strip() == "":
            return default
        num = int(float(val))
        return max(0, num)
    except (ValueError, TypeError):
        return default

def check_id(request):
    username = request.GET.get('username', None)
    # 아이디가 존재하는지 확인 (존재하면 True, 없으면 False)
    exists = User.objects.filter(username__iexact=username).exists()
    return JsonResponse({'is_taken': exists})

# 2. 회원가입 로직 (수정됨)
def register_step1(request):
    if request.method == "POST":
        term1 = request.POST.get('term1')
        term2 = request.POST.get('term2')
        term_sub1 = request.POST.get('term_sub1')
        if term1 and term2 and term_sub1:
            return render(request, 'auth_mypage/register_step2.html')
    return render(request, 'auth_mypage/register_step1.html')

def register_step2(request):
    if request.method == "POST":
        # step2 데이터를 세션에 저장
        request.session['step2_data'] = {
            'name': request.POST.get('name'),
            'username': request.POST.get('username'),
            'password': request.POST.get('password'),
            'email': request.POST.get('email'),
            'sido': request.POST.get('sido'),
            'sigungu': request.POST.get('sigungu'),
        }
        return redirect('policy:register_step3') # 스텝 3로 이동
    return render(request, 'auth_mypage/register_step2.html')

def register_step3(request):
    if request.method == "POST":
        step2_data = request.session.get('step2_data')
        
        # 세션이 만료된 경우 step1으로 리다이렉트하여 오류 방지
        if not step2_data:
            return redirect('policy:register_step1')
        
        
        # 1. User 생성
        user = User.objects.create_user(
            username=step2_data['username'],
            password=step2_data['password'],
            email=step2_data.get('email', ''),
            last_name=step2_data['name']
        )
        
        # 2. UserProfile 생성 및 Step 3 데이터 저장 (보안 검증 적용)
        UserProfile.objects.create(
            user=user,
            sido=step2_data['sido'],
            sigungu=step2_data['sigungu'],
            age=to_pos_int(request.POST.get('age')),
            income=to_pos_int(request.POST.get('income')),
            net_assets=to_pos_int(request.POST.get('net_assets')),
            debt=to_pos_int(request.POST.get('debt')),
            subscription_count=to_pos_int(request.POST.get('subscription_count')),
            subscription_amount=to_pos_int(request.POST.get('subscription_amount')),
            marital_status=request.POST.get('marital_status') if request.POST.get('marital_status') in VALID_MARITAL_STATUSES else "미혼",
            children_count=to_pos_int(request.POST.get('children_count'), 0),
            homeless_period=to_pos_int(request.POST.get('homeless_period')),
            is_pregnant=request.POST.get('is_pregnant') == 'True',
            is_first_home=request.POST.get('is_first_home') == 'True',
            is_homeless=request.POST.get('is_homeless') == 'True',
        )
        
        # 회원가입 완료 후 자동 로그인 처리
        user = authenticate(username=step2_data['username'], password=step2_data['password'])
        if user is not None:
            login(request, user)
        else:
            # 자동 로그인 실패 시 (예: 비밀번호 해싱 문제 등)
            # 이 경우에도 사용자에게 피드백을 주거나, 로그인 페이지로 리다이렉트 시 메시지를 전달할 수 있습니다.
            # 현재는 단순히 세션 비우고 홈으로 이동합니다.
            pass

        # 세션 비우고 index가 아닌 home으로 이동
        del request.session['step2_data']
        return redirect('home')
        
    return render(request, 'auth_mypage/register_step3.html')
# 3. 로그인/로그아웃 뷰 (기존 유지)
def id_login_view(request):
    if request.method == "POST":
        uid = request.POST.get('username')
        upw = request.POST.get('password')
        user = authenticate(request, username=uid, password=upw)
        if user:
            login(request, user)
            return redirect('home')
        else:
            error_message = "아이디 또는 비밀번호가 올바르지 않습니다."
            return render(request, 'auth_mypage/id_login.html', {'error': error_message})
    # GET 요청 시 로그인 폼 페이지를 보여줌
    return render(request, 'auth_mypage/id_login.html')

def logout_view(request):
    logout(request)
    # 로그아웃 후 세션 데이터 완전 삭제
    request.session.flush()
    return redirect('home')

# 4. 기본 페이지들 (수정됨)
def home(request):
    # 로그아웃 상태에서 template이 user.policy_profile에 접근해 에러나는 것을 방지
    profile = None
    if request.user.is_authenticated:
        try:
            profile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            profile = None

    context = {
        'profile': profile,
        'is_authenticated': request.user.is_authenticated or request.session.get('is_guest', False)
    }
    return render(request, 'auth_mypage/home.html', context)

def youth_home(request): return render(request, 'auth_mypage/youth_page.html')
def newlywed_home(request): return render(request, 'auth_mypage/newlywed_page.html')
def login_view(request): return render(request, 'auth_mypage/login.html')

def guest_login_view(request):
    if request.method == "POST":
        g_name = request.POST.get('guest_name', 'Guest')
        g_sido = request.POST.get('sido')
        g_sigungu = request.POST.get('sigungu')
        
        request.session['is_guest'] = True
        request.session['guest_name'] = g_name
        request.session['guest_sido'] = g_sido
        request.session['guest_sigungu'] = g_sigungu
        
        return redirect('home')
    return render(request, 'auth_mypage/guest_login.html')

# 5. [수정됨] 네이버 로그인 연결 (allauth 방식)
# 기존의 복잡한 naver_callback 함수를 삭제했습니다.
def naver_login_view(request):
    return redirect('/accounts/naver/login/')

# views.py의 mypage_view 부분을 아래로 교체
def mypage_view(request):
    user_info = {}
    
    if request.user.is_authenticated:
        try:
            profile = UserProfile.objects.get(user=request.user)
            
            # 뒷자리 마스킹 처리 함수 (음수 및 비정상 데이터 방어 포함)
            def mask_val(val, unit=""):
                if val is None or val == "": return "미설정"
                # 음수 방어
                if isinstance(val, int) and val < 0:
                    val = 0
                s = str(val)
                if s.isdigit() or (s.startswith('-') and s[1:].isdigit()):
                    num_val = int(s)
                    if num_val < 0: s = "0"
                
                if len(s) > 1:
                    return s[:-2] + "** " + unit
                return "* " + unit

            user_info = {
                'username': request.user.username,
                'name': request.user.last_name or "이름 미설정",
                'age': profile.age if profile.age else "미설정",
                'sido': profile.sido or "정보 없음",
                'sigungu': profile.sigungu or "정보 없음",
                'user_type': '정회원',
                # 마스킹 처리 항목들
                'password': "********",
                'income': mask_val(profile.income, "만원"),
                'net_assets': mask_val(profile.net_assets, "만원"),
                'debt': mask_val(profile.debt, "만원"),
                'sub_count': mask_val(profile.subscription_count, "회"),
                'sub_amount': mask_val(profile.subscription_amount, "만원"),
                'children': mask_val(profile.children_count, "명"),
                'homeless': mask_val(profile.homeless_period, "년"),
                'marital': profile.marital_status if profile.marital_status in VALID_MARITAL_STATUSES else "미설정",
            }
        except UserProfile.DoesNotExist:
            user_info = {'username': request.user.username, 'user_type': '정회원(프로필 없음)'}
            
    elif request.session.get('is_guest'):
        user_info = {
            'username': '비회원',
            'name': request.session.get('guest_name', '게스트'),
            'sido': request.session.get('guest_sido', '정보 없음'),
            'sigungu': request.session.get('guest_sigungu', '정보 없음'),
            'user_type': '비회원'
        }
    else:
        return redirect('policy:id_login')

    return render(request, 'auth_mypage/mypage.html', {'user_info': user_info})
            
# views.py 하단에 추가
def edit_profile_view(request):
    if not request.user.is_authenticated:
        return redirect('policy:login')
    
    profile = UserProfile.objects.get(user=request.user)

    if request.method == "POST":
        # 1. User 모델 정보 업데이트 (이름)
        request.user.last_name = request.POST.get('name')
        request.user.save()
        
        # 2. UserProfile 모델 정보 업데이트 (보안 검증 적용)
        profile.sido = request.POST.get('sido')
        profile.sigungu = request.POST.get('sigungu')
        profile.age = to_pos_int(request.POST.get('age'))
        profile.income = to_pos_int(request.POST.get('income'))
        profile.net_assets = to_pos_int(request.POST.get('net_assets'))
        profile.debt = to_pos_int(request.POST.get('debt'))
        profile.subscription_count = to_pos_int(request.POST.get('subscription_count'))
        profile.subscription_amount = to_pos_int(request.POST.get('subscription_amount'))
        profile.marital_status = request.POST.get('marital_status') if request.POST.get('marital_status') in VALID_MARITAL_STATUSES else "미혼"
        profile.children_count = to_pos_int(request.POST.get('children_count'), 0)
        profile.homeless_period = to_pos_int(request.POST.get('homeless_period'))
        
        profile.save()
        return redirect('policy:mypage')

    return render(request, 'auth_mypage/edit_profile.html', {'profile': profile})