import os
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('youth_road.urls')), # 🧭 루트로 즉시 연결
    path('chatbot/', include('chatbot.config.urls')), # 🤖 지능형 챗봇 프로젝트 통합
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
    urlpatterns += static('/media/', document_root=os.path.join(settings.BASE_DIR, 'media'))
