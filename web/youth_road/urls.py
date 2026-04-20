from django.urls import path
from django.views.generic import RedirectView
from . import views

# 🧭 청춘로(路) 순수 장고 뷰 주소 체계
urlpatterns = [
    path('', RedirectView.as_view(url='/', permanent=False), name='index'), # 랜딩 페이지
    path('diagnose/', RedirectView.as_view(url='/#form-anchor', permanent=False), name='diagnose'), # 지능형 진단
    path('result/<int:pk>/', RedirectView.as_view(url='/', permanent=False), name='result'), # 분석 결과 대시보드
    
    # 🔐 인증 및 회원 관리 (Auth System)
    path('signup/', RedirectView.as_view(url='/auth/register/', permanent=False), name='signup'),
    path('login/', RedirectView.as_view(url='/auth/login/', permanent=False), name='login'),
    path('logout/', RedirectView.as_view(url='/auth/logout/', permanent=False), name='logout'),
    path('my-reports/', RedirectView.as_view(pattern_name='myreport', permanent=False), name='my_reports'), # 내 리포트 보관함
]

