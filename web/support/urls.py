from django.urls import path
from . import views

app_name = 'support'

urlpatterns = [
    path('', views.support_home, name='support_home'),
    path('notice/', views.notice_list, name='notice_list'),
    path('notice/<int:pk>/', views.notice_detail, name='notice_detail'),
    path('inquiry/', views.inquiry_list, name='inquiry_list'),
    path('inquiry/new/', views.inquiry_create, name='inquiry_create'),
    
    # Real-time Chat URLs
    path('chat/', views.chat_room, name='chat_room'),
    path('admin/chat/', views.admin_chat_list, name='admin_chat_list'),
    path('admin/chat/<int:room_id>/', views.admin_chat_detail, name='admin_chat_detail'),
    
    # Chat API
    path('api/chat/<int:room_id>/send/', views.api_send_message, name='api_send_message'),
    path('api/chat/<int:room_id>/messages/', views.api_get_messages, name='api_get_messages'),
]
