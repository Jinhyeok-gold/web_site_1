from django.core.management.base import BaseCommand
from youth_road.models import FinanceProduct, WelfareProduct, HousingProduct
from datetime import date, timedelta

class Command(BaseCommand):
    help = "Seed core youth policies (Rentals, Savings) with real URLs"

    def handle(self, *args, **options):
        # 1. Housing Products (Targeting the user's Profile: Seoul, 30M income)
        today = date.today()
        housing_data = [
            {
                "product_id": "HOU-SEOUL-RENTAL-TOP",
                "title": "[SH] 서울시 청년 임대주택 공고",
                "org": "SH 서울주택도시공사", "category": "공공임대", "region": "서울", 
                "sales_price": 5000, "notice_date": today - timedelta(days=1), "end_date": today + timedelta(days=20),
                "url": "https://www.i-sh.co.kr/main/lay2/program/S1T294C295/www/brd/m_241/list.do", "is_active": True
            },
            {
                "product_id": "HOU-PRIVATE-PRE",
                "title": "강남 반포 자이 더퍼스트 민영 분양",
                "org": "GS건설", "category": "민영분양", "region": "서울", 
                "sales_price": 150000, # 15억 (80M 소득자에게 현실적인 시뮬레이션용)
                "notice_date": today - timedelta(days=5), "end_date": today + timedelta(days=10),
                "url": "https://www.applyhome.co.kr/", "is_active": True
            }
        ]
        
        finance_data = [
            {"product_id": "FIN-YOUTH-LEAP", "title": "청년도약계좌 (정부지원)", "bank_nm": "전국 주요 은행", "category": "적금/저축", "base_rate": 5.0, "target_desc": "연소득 7,500만원 이하 청년", "notice_date": today - timedelta(days=5), "url": "https://www.kinfa.or.kr/", "is_active": True},
            {"product_id": "FIN-GENERAL-LOAN", "title": "청춘로 전용 내집마련 신용대출", "bank_nm": "우리은행", "category": "신용대출", "base_rate": 4.2, "target_desc": "소득 제한 없음, 우수 고객 전용", "notice_date": today - timedelta(days=1), "url": "https://www.wooribank.com/", "is_active": True}
        ]
        
        welfare_data = [
            {"policy_id": "WEL-SEOUL-MONTHLY", "title": "2024 서울 청년 월세 지원", "org_nm": "서울특별시", "category": "월세지원", "benefit_desc": "월 20만원 지원", "target_desc": "중위소득 150% 이하 (약 4,500만원 이하)", "region": "서울", "notice_date": today - timedelta(days=2), "end_date": today + timedelta(days=45), "url": "https://youth.seoul.go.kr/", "is_active": True},
            {"policy_id": "WEL-GENERAL-TAX", "title": "청년 소득세 감면 특별 혜택", "org_nm": "국세청", "category": "세제지원", "benefit_desc": "소득세 최대 90% 감면", "target_desc": "만 34세 이하 취업 청년 (소득 무관)", "region": "전국", "notice_date": today - timedelta(days=100), "url": "https://www.nts.go.kr/", "is_active": True}
        ]

        for item in housing_data: 
            HousingProduct.objects.update_or_create(manage_no=item['product_id'], defaults={
                'title': item['title'], 'org': item['org'], 'category': item['category'],
                'region': item['region'], 'notice_date': item['notice_date'], 
                'end_date': item['end_date'], 'url': item['url'], 'is_active': item['is_active']
            })
        for item in finance_data: FinanceProduct.objects.update_or_create(product_id=item['product_id'], defaults=item)
        for item in welfare_data: WelfareProduct.objects.update_or_create(policy_id=item['policy_id'], defaults=item)
        
        self.stdout.write(self.style.SUCCESS("Successfully seeded FRESH policies!"))
