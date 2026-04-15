from django.contrib import admin
from .models import UserProfile

# UserProfile 모델을 관리자 페이지에 등록합니다.
admin.site.register(UserProfile)