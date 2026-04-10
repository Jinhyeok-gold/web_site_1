from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.http import JsonResponse

# 아이디 중복 확인 함수
def check_id(request):
    username = request.GET.get('username', None)
    # 아이디가 존재하는지 확인 (있으면 True, 없으면 False)
    data = {
        'is_taken': User.objects.filter(username__iexact=username).exists()
    }
    return JsonResponse(data)

# 회원정보 입력 및 저장 함수
def register_step2(request):
    if request.method == "POST":
        uid = request.POST.get('username')
        upw = request.POST.get('password')
        uname = request.POST.get('name')
        
        # 1. 아이디 중복 한 번 더 체크 (보안상 필요)
        if User.objects.filter(username=uid).exists():
            return render(request, 'policyapp/register_step2.html', {'error': '이미 존재하는 아이디입니다.'})
        
        # 2. 유저 생성 및 저장 (비밀번호는 암호화됨)
        # last_name에 이름을 저장하는 예시입니다.
        User.objects.create_user(username=uid, password=upw, last_name=uname)
        
        # 3. 가입 완료 후 로그인 페이지로 이동
        return redirect('login') 
        
    # GET 방식일 때는 페이지를 그냥 보여줌
    return render(request, 'policyapp/register_step2.html')

def index(request):
    return render(request, 'policyapp/index.html')

def youth_home(request):
    return render(request, 'policyapp/youth_page.html')

# policyapp/views.py (기존 파일 하단에 추가)

def newlywed_home(request):
    # 아직 html 파일을 안 만드셨다면, 일단 청년 페이지나 index를 띄우게 설정해도 됩니다.
    # 여기서는 새로 만들 'newlywed_page.html'을 부른다고 가정합니다.
    return render(request, 'policyapp/newlywed_page.html')

# policyapp/views.py

def login_view(request):
    return render(request, 'policyapp/login.html')
# policyapp/views.py

def id_login_view(request):
    return render(request, 'policyapp/id_login.html')
# policyapp/views.py
def qr_login_view(request):
    return render(request, 'policyapp/qr_login.html')
# policyapp/views.py
def guest_login_view(request):
    return render(request, 'policyapp/guest_login.html')

def register_step1(request):
    if request.method == "POST":
        # 필수 약관(term1, term2)이 체크되었는지 확인
        term1 = request.POST.get('term1')
        term2 = request.POST.get('term2')
        term_sub1 = request.POST.get('term_sub1')

        if term1 and term2 and term_sub1:
            # 필수 동의 완료 시 2단계로 이동
          return render(request, 'policyapp/register_step2.html')
        else:
            # 필수 항목 미체크 시 메시지와 함께 현재 페이지 유지
            return render(request, 'policyapp/register_step1.html', {'error': '필수 약관에 동의해주세요.'})
            
    return render(request, 'policyapp/register_step1.html')

def register_step2(request):
    # 회원정보 입력 페이지
    return render(request, 'policyapp/register_step2.html')