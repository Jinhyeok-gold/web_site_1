from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from youth_road.models import HousingProduct, FinanceProduct, WelfareProduct
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Notice, FAQ, Inquiry, ChatRoom, ChatMessage
import json
from datetime import date

def sync_latest_policies_to_notices():
    """최신 정책/혜택 데이터를 공지사항으로 실시간 동기화 및 만료 관리"""
    today = date.today()
    
    # 1. 만료된 공지사항 자동 청소 (Cleanup)
    # [실시간]으로 시작하는 공지 중 기간이 지났거나 더 이상 유효하지 않은 데이터를 우선 정리
    # (효율적인 관리를 위해 매 접속 시 만료된 공지는 보이지 않게 처리)
    Notice.objects.filter(title__startswith="[실시간", created_at__date__lt=today).delete()

    # 2. 현재 모집 중인 최신 데이터 추출
    active_filter = Q(end_date__gte=today) | Q(end_date__isnull=True)
    
    latest_housing = HousingProduct.objects.filter(active_filter, is_active=True).order_by('-notice_date')[:2]
    latest_finance = FinanceProduct.objects.filter(active_filter, is_active=True).order_by('-notice_date')[:2]
    latest_welfare = WelfareProduct.objects.filter(active_filter, is_active=True).order_by('-notice_date')[:2]
    
    sync_targets = [
        (latest_housing, "[실시간 주거]"),
        (latest_finance, "[실시간 금융]"),
        (latest_welfare, "[실시간 혜택]")
    ]
    
    for queryset, prefix in sync_targets:
        for item in queryset:
            # 필드 값 추출 및 검증
            org = getattr(item, 'org', None) or getattr(item, 'bank_nm', None) or getattr(item, 'org_nm', None) or '확인 필요'
            region = getattr(item, 'region', '전국')
            benefit = getattr(item, 'benefit_desc', None) or getattr(item, 'target_desc', None)
            url = getattr(item, 'url', None)
            
            # 기간 정보 추출
            start_dt = getattr(item, 'start_date', None) or getattr(item, 'notice_date', None)
            end_dt = getattr(item, 'end_date', None)
            period = f"{start_dt or '상시'} ~ {end_dt or '마감 시까지'}"
            if end_dt:
                days_left = (end_dt - today).days
                if 0 <= days_left <= 7:
                    period += f" (종료 {days_left}일 전! 🔥)"

            # [STRICT FILTER] 상세 내용과 URL이 둘 다 없으면 제외
            if not benefit and not url:
                continue
                
            if not url or url.lower() == 'none' or url == '#':
                url = "https://www.youthroad.go.kr (공고문 별도 확인)"

            item_title = getattr(item, 'title', '')
            title = f"{prefix} {item_title}"
            
            # 중복 생성 방지 (오늘 이미 생성된 동일 제목은 건너뜀)
            if not Notice.objects.filter(title=title, created_at__date=today).exists():
                # 본문 구성 (가장 중요한 정보인 기간과 자격을 최상단에 배치)
                content = f"📢 [가장 중요한 정보]\n"
                content += f"● 모집 기간: {period}\n"
                target_info = getattr(item, 'target_desc', '상세 공고 참조')
                if len(target_info) > 100: target_info = target_info[:100] + "..."
                content += f"● 지원 대상: {target_info}\n\n"
                
                content += f"● 공급 기관: {org}\n"
                content += f"● 지역 범위: {region}\n\n"
                content += f"● 상세 혜택 소식:\n{benefit or '공식 공고문을 참조해 주시기 바랍니다.'}\n\n"
                content += f"● 공식 공고문 및 신청 링크:\n{url}"
                
                # 중요 공지로 등록하여 실시간 노출
                Notice.objects.create(
                    title=title,
                    content=content,
                    is_important=True
                )

def support_home(request):
    """고객센터 메인 페이지 (지능형 라이프사이클 관리 포함)"""
    try:
        sync_latest_policies_to_notices()
    except Exception:
        pass
        
    # 중요 공지 우선, 최신순 10개
    notices = Notice.objects.all().order_by('-is_important', '-created_at')[:10]
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

def notice_list(request):
    """전체 공지사항 목록 페이지"""
    all_notices = Notice.objects.all().order_by('-is_important', '-created_at')
    return render(request, 'support/notice_list.html', {'all_notices': all_notices})

def notice_detail(request, pk):
    """공지사항 상세"""
    notice = Notice.objects.get(pk=pk)
    return render(request, 'support/notice_detail.html', {'notice': notice})

@login_required
def chat_room(request):
    """고객용 채팅방 입장 및 생성 (전용 페이지)"""
    # 기존 활성 상담방 찾기
    chat_room = ChatRoom.objects.filter(customer=request.user, status__in=['PENDING', 'ACTIVE']).first()
    
    # 없으면 새로 생성
    if not chat_room:
        chat_room = ChatRoom.objects.create(customer=request.user)
    
    # 진단 데이터 가져오기 (사이드바용)
    from youth_road.models import UserDiagnostic
    diagnostic = UserDiagnostic.objects.filter(user=request.user).order_by('-created_at').first()
    
    context = {
        'room': chat_room,
        'diagnostic': diagnostic,
    }
    return render(request, 'support/chat.html', context)

@login_required
def admin_chat_list(request):
    """상담사용 대시보드 (진행 중인 모든 상담 목록)"""
    if not request.user.is_staff:
        return redirect('support:support_home')
        
    pending_rooms = ChatRoom.objects.filter(status='PENDING').order_by('created_at')
    active_rooms = ChatRoom.objects.filter(status='ACTIVE', counselor=request.user).order_by('-updated_at')
    
    return render(request, 'support/admin_chat_list.html', {
        'pending_rooms': pending_rooms,
        'active_rooms': active_rooms
    })

@login_required
def admin_chat_detail(request, room_id):
    """상담사 전용 채팅 상세 화면"""
    if not request.user.is_staff:
        return redirect('support:support_home')
        
    room = ChatRoom.objects.get(id=room_id)
    
    # 상담사가 없는 빈 방인 경우, 현재 상담사가 참여 처리
    if room.status == 'PENDING':
        room.counselor = request.user
        room.status = 'ACTIVE'
        room.save()
        
    # 고객의 진단 데이터
    from youth_road.models import UserDiagnostic
    diagnostic = UserDiagnostic.objects.filter(user=room.customer).order_by('-created_at').first()
    
    return render(request, 'support/admin_chat_detail.html', {
        'room': room,
        'diagnostic': diagnostic
    })

@csrf_exempt
@login_required
def api_send_message(request, room_id):
    """메시지 전송 API"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            content = data.get('content')
            if not content:
                return JsonResponse({'error': 'Content is missing'}, status=400)
                
            room = ChatRoom.objects.get(id=room_id)
            
            # [v22] 종료된 상담방 방어 로직
            if room.status == 'CLOSED':
                return JsonResponse({'error': '이미 종료된 상담입니다.'}, status=403)
                
            ChatMessage.objects.create(
                room=room,
                sender=request.user,
                message=content
            )
            # 최종 활동 시간 업데이트
            room.save() 
            
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def api_get_messages(request, room_id):
    """새 메시지 목록 조회 API (Polling용)"""
    last_id = request.GET.get('last_id', 0)
    messages = ChatMessage.objects.filter(room_id=room_id, id__gt=last_id).order_by('timestamp')
    
    data = []
    for m in messages:
        data.append({
            'id': m.id,
            'sender': m.sender.username,
            'is_me': m.sender == request.user,
            'is_staff': m.sender.is_staff,
            'message': m.message,
            'timestamp': m.timestamp.strftime('%H:%M')
        })
    return JsonResponse({'messages': data})

@csrf_exempt
@login_required
def api_close_chat(request, room_id):
    """상담 종료 API (v22)"""
    if request.method == 'POST':
        try:
            room = ChatRoom.objects.get(id=room_id)
            # 고객 본인이거나 상담사인 경우에만 종료 가능
            if room.customer == request.user or (request.user.is_staff and room.counselor == request.user):
                room.status = 'CLOSED'
                room.save()
                
                # 시스템 종료 메시지 기록
                ChatMessage.objects.create(
                    room=room,
                    sender=request.user,
                    message="[시스템] 상담이 종료되었습니다."
                )
                
                return JsonResponse({'status': 'success'})
            else:
                return JsonResponse({'error': '권한이 없습니다.'}, status=403)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request'}, status=400)
