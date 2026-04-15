"""
URL configuration for mypolicy project.
"""
from django.contrib import admin
from django.urls import path, include
from policyapp import views  # policyapp의 views를 직접 가져옵니다.

urlpatterns = [
    # 1. 관리자 및 인증 관련
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),

    # 2. 메인 페이지 및 정책 관련 (views.py의 함수와 직접 연결)
    path('', views.index, name='index'),
    path('youth/', views.youth_home, name='youth_home'),
    path('newlywed/', views.newlywed_home, name='newlywed_home'),

    # 3. 로그인/회원가입 관련
    path('login/', views.login_view, name='login'),
    path('login/id/', views.id_login_view, name='id_login'),
    path('logout/', views.logout_view, name='logout'),
    path('login/naver/', views.naver_login_view, name='naver_login'),
    path('login/guest/', views.guest_login_view, name='guest_login'),
    path('register/', views.register_step1, name='register_step1'),
    path('register/step2/', views.register_step2, name='register_step2'),
    path('register/step3/', views.register_step3, name='register_step3'),
    path('check-id/', views.check_id, name='check_id'),
    path('mypage/', views.mypage_view, name='mypage'),
    path('edit_profile/', views.edit_profile_view, name='edit_profile'),
    
    # 중복되었던 'login/guest/' 경로는 하나로 합쳤습니다.
]