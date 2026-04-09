from django.urls import path
from . import views

urlpatterns = [
    path('api/policies/', views.match_policies, name='match_policies'),
    path('api/chat/', views.chat_gemini, name='chat_gemini'),
    path('api/ai-report/', views.get_ai_report, name='ai_report'),
]
