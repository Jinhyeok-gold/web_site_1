from django.urls import path
from . import views

app_name = 'support'

urlpatterns = [
    path('', views.support_home, name='support_home'),
    path('notice/<int:pk>/', views.notice_detail, name='notice_detail'),
    path('inquiry/', views.inquiry_list, name='inquiry_list'),
    path('inquiry/new/', views.inquiry_create, name='inquiry_create'),
]
