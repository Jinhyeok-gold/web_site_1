from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse

# 1. 아이디 중복 확인
def check_id(request):
    username = request.GET.get('username', None)
    data = {
        'is_taken': User.objects.filter(username__iexact=username).exists()
    }
    return JsonResponse(data)

# 2. 회원가입 저장 로직 (하나로 통합)
def register_step2(request):
    if request.method == "POST":
        uid = request.POST.get('username')
        upw = request.POST.get('password')
        uname = request.POST.get('name')
        
        if User.objects.filter(username=uid).exists():
            return render(request, 'myproject/register_step2.html', {'error': '이미 존재하는 아이디입니다.'})
        
        # 유저 생성 및 데이터베이스 저장 (성명은 last_name에 저장하여 '환영합니다' 문구와 연동)
        User.objects.create_user(username=uid, password=upw, last_name=uname)
        return redirect('portal:id_login') 
        
    return render(request, 'myproject/register_step2.html')

# 3. 로그인 기능 (실제 세션 생성)
def id_login_view(request):
    if request.method == "POST":
        uid = request.POST.get('username')
        upw = request.POST.get('password')
        
        user = authenticate(request, username=uid, password=upw)
        
        if user is not None:
            login(request, user)  # 로그인 처리
            return redirect('home') # 메인 대시보드로 이동
        else:
            return render(request, 'myproject/id_login.html', {'error': '아이디 또는 비밀번호가 틀렸습니다.'})
            
    return render(request, 'myproject/id_login.html')

# 4. 로그아웃 기능
def logout_view(request):
    logout(request)
    request.session.flush()
    return redirect('home')

# 나머지 페이지 뷰들 (새로운 템플릿 경로 myproject/ 적용)
def index(request): return render(request, 'myproject/index.html')
def youth_home(request): return render(request, 'myproject/youth_page.html')
def newlywed_home(request): return render(request, 'myproject/newlywed_page.html')
def login_view(request): return render(request, 'myproject/login.html')
def qr_login_view(request): return render(request, 'myproject/qr_login.html')

def register_step1(request):
    if request.method == "POST":
        term1 = request.POST.get('term1')
        term2 = request.POST.get('term2')
        term_sub1 = request.POST.get('term_sub1')
        if term1 and term2 and term_sub1:
            return render(request, 'myproject/register_step2.html')
        else:
            return render(request, 'myproject/register_step1.html', {'error': '필수 약관에 동의해주세요.'})
    return render(request, 'myproject/register_step1.html')

def guest_login_view(request):
    if request.method == "POST":
        g_name = request.POST.get('guest_name', 'Guest')
        request.session['is_guest'] = True
        request.session['guest_name'] = g_name
        return redirect('home')
    return render(request, 'myproject/guest_login.html')