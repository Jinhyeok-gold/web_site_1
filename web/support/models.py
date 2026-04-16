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

class ChatRoom(models.Model):
    """실시간 상담 채팅방"""
    STATUS_CHOICES = [
        ('PENDING', '상담 대기'),
        ('ACTIVE', '상담 중'),
        ('CLOSED', '상담 종료'),
    ]
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_rooms_as_customer', verbose_name="고객")
    counselor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='chat_rooms_as_counselor', verbose_name="상담사")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING', verbose_name="상담 상태")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="최종 활동")

    class Meta:
        verbose_name = "채팅 상담방"
        verbose_name_plural = "채팅 상담방 목록"
        ordering = ['-updated_at']

    def __str__(self):
        counselor_name = self.counselor.username if self.counselor else "미배정"
        return f"[{self.get_status_display()}] {self.customer.username}님 상담 ({counselor_name})"

class ChatMessage(models.Model):
    """채팅 메시지 내역"""
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages', verbose_name="채팅방")
    sender = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="발신자")
    message = models.TextField(verbose_name="메시지 내용")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="전송 시간")
    is_read = models.BooleanField(default=False, verbose_name="읽음 여부")

    class Meta:
        verbose_name = "채팅 메시지"
        verbose_name_plural = "채팅 메시지 목록"
        ordering = ['timestamp']

    def __str__(self):
        return f"[{self.sender.username}] {self.message[:20]}"
