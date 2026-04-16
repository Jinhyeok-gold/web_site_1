from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Notice, FAQ, Inquiry
from django.contrib import messages
from django.utils import timezone

def support_home(request):
    """고객센터 메인 페이지"""
    notices = Notice.objects.all()[:5]
    faqs = FAQ.objects.all()[:10]
    
    context = {
        'notices': notices,
        'faqs': faqs,
    }
    return render(request, 'support/home.html', context)

@login_required
def inquiry_list(request):
    """나의 문의 내역"""
    inquiries = Inquiry.objects.filter(user=request.user)
    return render(request, 'support/inquiry_list.html', {'inquiries': inquiries})

@login_required
def inquiry_create(request):
    """1:1 문의 작성"""
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        
        if title and content:
            Inquiry.objects.create(
                user=request.user,
                title=title,
                content=content
            )
            messages.success(request, "문의가 정상적으로 등록되었습니다.")
            return redirect('support:support_home')
        else:
            messages.error(request, "제목과 내용을 모두 입력해주세요.")
            
    return render(request, 'support/inquiry_form.html')

def notice_detail(request, pk):
    """공지사항 상세"""
    notice = Notice.objects.get(pk=pk)
    return render(request, 'support/notice_detail.html', {'notice': notice})
