from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('dashboard/', views.index, name='portal_dashboard'),
    path('youth/', views.youth_home, name='youth_home'),
    path('newlywed/', views.newlywed_home, name='newlywed_home'),
    path('login/', views.login_view, name='login'),
    path('id_login/', views.id_login_view, name='id_login'),
    path('qr_login/', views.qr_login_view, name='qr_login'),
    path('guest_login/', views.guest_login_view, name='guest_login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/step1/', views.register_step1, name='register_step1'),
    path('register/step2/', views.register_step2, name='register_step2'),
    path('api/check-id/', views.check_id, name='check_id'),
]
