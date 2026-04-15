from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse, HttpResponse
# requests와 uuid는 더 이상 필요 없으므로 삭제했습니다.
from .models import UserProfile
from django.http import JsonResponse
from django.contrib.auth.models import User

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
            return render(request, 'policyapp/register_step2.html')
    return render(request, 'policyapp/register_step1.html')

def register_step2(request):
    if request.method == "POST":
        # step2 데이터를 세션에 저장
        request.session['step2_data'] = {
            'name': request.POST.get('name'),
            'username': request.POST.get('username'),
            'password': request.POST.get('password'),
            'sido': request.POST.get('sido'),
            'sigungu': request.POST.get('sigungu'),
        }
        return redirect('policy:register_step3') # 스텝 3로 이동
    return render(request, 'policyapp/register_step2.html')

def register_step3(request):
    if request.method == "POST":
        step2_data = request.session.get('step2_data')
        
        
        # 1. User 생성
        user = User.objects.create_user(
            username=step2_data['username'],
            password=step2_data['password'],
            last_name=step2_data['name']
        )
        
        # 2. UserProfile 생성 및 Step 3 데이터 저장
        UserProfile.objects.create(
            user=user,
            sido=step2_data['sido'],
            sigungu=step2_data['sigungu'],
            age=request.POST.get('age'),
            income=request.POST.get('income'),
            net_assets=request.POST.get('net_assets'),
            debt=request.POST.get('debt'),
            subscription_count=request.POST.get('subscription_count'),
            subscription_amount=request.POST.get('subscription_amount'),
            marital_status=request.POST.get('marital_status'),
            children_count=request.POST.get('children_count'),
            homeless_period=request.POST.get('homeless_period'),
            is_pregnant=request.POST.get('is_pregnant') == 'True',
            is_first_home=request.POST.get('is_first_home') == 'True',
            is_homeless=request.POST.get('is_homeless') == 'True',
        )
        
        # 세션 비우고 로그인 페이지로
        del request.session['step2_data']
        return redirect('policy:id_login')
        
    return render(request, 'policyapp/register_step3.html')
# 3. 로그인/로그아웃 뷰 (기존 유지)
def id_login_view(request):
    if request.method == "POST":
        uid = request.POST.get('username')
        upw = request.POST.get('password')
        user = authenticate(request, username=uid, password=upw)
        if user:
            login(request, user)
            return redirect('policy:index')
    return render(request, 'policyapp/id_login.html')

def logout_view(request):
    logout(request)
    request.session.flush()
    return redirect('policy:index')

# 4. 기본 페이지들 (수정됨)
def index(request): return render(request, 'policyapp/index.html')
def youth_home(request): return render(request, 'policyapp/youth_page.html')
def newlywed_home(request): return render(request, 'policyapp/newlywed_page.html')
def login_view(request): return render(request, 'policyapp/login.html')

def guest_login_view(request):
    if request.method == "POST":
        g_name = request.POST.get('guest_name', 'Guest')
        g_sido = request.POST.get('sido')
        g_sigungu = request.POST.get('sigungu')
        
        request.session['is_guest'] = True
        request.session['guest_name'] = g_name
        request.session['guest_sido'] = g_sido
        request.session['guest_sigungu'] = g_sigungu
        
        return redirect('policy:index')
    return render(request, 'policyapp/guest_login.html')

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
            
            # 뒷자리 마스킹 처리 함수
            def mask_val(val, unit=""):
                if val is None or val == "": return "미설정"
                s = str(val)
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
                'marital': profile.marital_status or "미설정",
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

    return render(request, 'policyapp/mypage.html', {'user_info': user_info})
            
# views.py 하단에 추가
def edit_profile_view(request):
    if not request.user.is_authenticated:
        return redirect('policy:login')
    
    profile = UserProfile.objects.get(user=request.user)

    if request.method == "POST":
        # 1. User 모델 정보 업데이트 (이름)
        request.user.last_name = request.POST.get('name')
        request.user.save()
        
        # 2. UserProfile 모델 정보 업데이트 (상세 정보 전체)
        profile.sido = request.POST.get('sido')
        profile.sigungu = request.POST.get('sigungu')
        profile.age = request.POST.get('age') or None
        profile.income = request.POST.get('income') or None
        profile.net_assets = request.POST.get('net_assets') or None
        profile.debt = request.POST.get('debt') or None
        profile.subscription_count = request.POST.get('subscription_count') or None
        profile.subscription_amount = request.POST.get('subscription_amount') or None
        profile.marital_status = request.POST.get('marital_status')
        profile.children_count = request.POST.get('children_count') or 0
        profile.homeless_period = request.POST.get('homeless_period') or None
        
        profile.save()
        return redirect('policy:mypage')

    return render(request, 'policyapp/edit_profile.html', {'profile': profile})