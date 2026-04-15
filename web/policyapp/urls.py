from django.urls import path
from . import views

app_name = 'policy'

urlpatterns = [
    path('', views.index, name='index'),
    path('youth/', views.youth_home, name='youth_home'),
    path('newlywed/', views.newlywed_home, name='newlywed_home'),
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
]
