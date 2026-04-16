import os
import sys
import django

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from support.models import FAQ, Notice

def seed_data():
    # FAQ 데이터
    faq_data = [
        ('POLICY', '어떤 정책이 저에게 맞는지 어떻게 아나요?', '메인 페이지의 "자가진단"을 완료해 보세요! 사용자님의 연령, 소득, 지역 데이터를 기반으로 AI가 가장 적합한 정책 TOP 3를 실시간으로 찾아드립니다.'),
        ('FINANCE', '신생아 특례 대출 금리는 얼마인가요?', '최저 연 1.6%의 저금리로 지원됩니다. 단, 합산 연소득 1.3억원 이하, 자산 4.69억원 이하 등의 요건을 충족해야 합니다.'),
        ('USAGE', '진단 결과 리포트를 이메일로 받고 싶어요.', '결과 대치보드 하단의 "내 이메일로 발송" 버튼을 누르시면 PDF 형태의 정밀 분석 리포트가 전송됩니다. (로그인 필요)'),
        ('POLICY', '무주택 기간은 어떻게 계산하나요?', '만 30세가 된 날과 혼인신고일 중 빠른 날을 기준으로 계산합니다. 단, 그 전 주택 소유 이력이 있다면 마지막으로 처분하여 무주택이 된 날부터 기산합니다.'),
    ]

    for cat, q, a in faq_data:
        FAQ.objects.get_or_create(category=cat, question=q, defaults={'answer': a})

    # 공지사항 데이터
    Notice.objects.get_or_create(
        title="[중요] 2024년 청년 매입임대주택 입주자 수시모집 안내",
        defaults={
            'content': "수도권 및 주요 광역시를 대상으로 청년 매입임대주택 입주자를 수시 모집합니다. 상세 공고는 LH 청약플러스를 확인하세요.",
            'is_important': True
        }
    )
    
    Notice.objects.get_or_create(
        title="딱맞춤 서비스 점검 및 고도화 작업 완료 (v20 Premium)",
        defaults={
            'content': "더 정확한 AI 매칭 엔진 업그레이드가 완료되었습니다. 이제 모바일에서도 최적화된 리포트를 확인하실 수 있습니다.",
            'is_important': False
        }
    )

    print("✅ 초기 지원 데이터 시딩 완료!")

if __name__ == "__main__":
    seed_data()
