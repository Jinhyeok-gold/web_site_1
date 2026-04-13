"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import os
from django.contrib import admin
from django.urls import path, include
from mainwindow import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('chatbot/', include('chatbot.core.urls')),
    path('portal/', include('myproject.urls')), # 포털 관련 기능은 /portal/ 또는 개별 경로로 접근
    path('myreport/', views.myreport, name='myreport'),
    path('welfare_map/', views.welfare_map, name='welfare_map'),
]

if settings.DEBUG:
    urlpatterns += static('/media/', document_root=os.path.join(settings.BASE_DIR, 'media'))