from django.db import models
from django.contrib.auth.models import User

class Notice(models.Model):
    """사이트 공지 및 긴급 정책 알림"""
    title = models.CharField(max_length=200, verbose_name="공지 제목")
    content = models.TextField(verbose_name="공지 내용")
    is_important = models.BooleanField(default=False, verbose_name="중요")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="작성일")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "공지사항"
        verbose_name_plural = "공지사항 목록"
        ordering = ['-is_important', '-created_at']

    def __str__(self):
        return self.title

class FAQ(models.Model):
    """자주 묻는 질문"""
    CATEGORY_CHOICES = [
        ('POLICY', '정책/주거'),
        ('FINANCE', '금융/대출'),
        ('USAGE', '사이트 이용'),
        ('OTHER', '기타'),
    ]
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, verbose_name="카테고리")
    question = models.CharField(max_length=200, verbose_name="질문")
    answer = models.TextField(verbose_name="답변")
    order = models.IntegerField(default=0, verbose_name="정렬 순서")

    class Meta:
        verbose_name = "자주 묻는 질문"
        verbose_name_plural = "자주 묻는 질문 목록"
        ordering = ['category', 'order']

    def __str__(self):
        return f"[{self.get_category_display()}] {self.question}"

class Inquiry(models.Model):
    """1:1 문의상담"""
    STATUS_CHOICES = [
        ('PENDING', '답변 대기'),
        ('ANSWERED', '답변 완료'),
        ('CLOSED', '상담 종료'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='inquiries', verbose_name="작성자")
    title = models.CharField(max_length=200, verbose_name="문의 제목")
    content = models.TextField(verbose_name="문의 내용")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING', verbose_name="상태")
    
    admin_answer = models.TextField(blank=True, null=True, verbose_name="관리자 답변")
    answered_at = models.DateTimeField(blank=True, null=True, verbose_name="답변 일시")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="작성일")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "1:1 문의"
        verbose_name_plural = "1:1 문의 목록"
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.get_status_display()}] {self.title}"
