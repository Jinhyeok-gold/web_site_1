from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    path('', views.index, name='chat_view'),
    path('api/policies/', views.match_policies, name='match_policies'),
    path('api/chat/', views.chat_gemini, name='chat_gemini'),
    path('api/ai-report/', views.get_ai_report, name='ai_report'),
    path('api/send-email/', views.send_user_report_email, name='send_email'),
    path('api/product-detail/', views.get_product_detail, name='product_detail'),
]

