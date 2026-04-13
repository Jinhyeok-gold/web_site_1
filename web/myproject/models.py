# policyapp/models.py 예시
from django.db import models
from django.contrib.auth.models import User

# 추가 정보가 필요하다면 프로필 모델을 만듭니다.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # 여기에 성별, 나이 등 추가하고 싶은 필드 작성
# Create your models here.
