from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='policy_profile')
    sido = models.CharField(max_length=50, blank=True, null=True)
    sigungu = models.CharField(max_length=50, blank=True, null=True)
    age = models.IntegerField(blank=True, null=True)
    income = models.IntegerField(blank=True, null=True)
    net_assets = models.IntegerField(blank=True, null=True)
    debt = models.IntegerField(blank=True, null=True)
    subscription_count = models.IntegerField(blank=True, null=True)
    subscription_amount = models.IntegerField(blank=True, null=True)
    marital_status = models.CharField(max_length=20, blank=True, null=True)
    children_count = models.IntegerField(default=0)
    homeless_period = models.IntegerField(blank=True, null=True)
    
    # 추가된 필드 (매칭용)
    is_pregnant = models.BooleanField(default=False, verbose_name="임신여부")
    is_first_home = models.BooleanField(default=True, verbose_name="생애최초 주택구입 여부")
    is_homeless = models.BooleanField(default=True, verbose_name="현재 무주택 여부")

    def __str__(self):
        return f"{self.user.username}의 프로필"