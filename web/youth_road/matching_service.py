from .models import HousingProduct, FinanceProduct, WelfareProduct
# from .firebase_service import FirebaseManager (Removed)
import random
from datetime import datetime, date, timedelta
from django.db.models import Q

class MatchingEngine:
    """청춘로 지능형 초정밀(Housing/Finance/Welfare) 매칭 엔진 v20 (17 Regions Edition)"""

    # 🗺️ 전국 17개 광역자치단체 키워드 매핑 (중앙 관리)
    REGION_KEYWORD_MAP = {
        'Seoul': '서울', 'Busan': '부산', 'Daegu': '대구', 'Incheon': '인천', 
        'Gwangju': '광주', 'Daejeon': '대전', 'Ulsan': '울산', 'Sejong': '세종', 
        'Gyeonggi': '경기', 'Gangwon': '강원', 'Chungbuk': '충북', 'Chungnam': '충남', 
        'Jeonbuk': '전북', 'Jeonnam': '전남', 'Gyeongbuk': '경북', 'Gyeongnam': '경남', 
        'Jeju': '제주'
    }
    
    @staticmethod
    def map_profile_to_instance(profile):
        """[Adapter] UserProfile(policyapp) 객체를 MatchingEngine용 가상 인스턴스로 변환"""
        # 간단한 가상 클래스 생성 (getattr 대응용)
        class VirtualInstance:
            def __init__(self, p):
                self.age = p.age or 29
                # 지역 매핑 (Sido 한글 -> Key)
                self.region = 'Seoul' # Default
                for k, v in MatchingEngine.REGION_KEYWORD_MAP.items():
                    if v in (p.sido or ""):
                        self.region = k
                self.sub_region = p.sigungu
                self.total_income = p.income or 3000
                self.assets = p.net_assets or 10000
                self.debt = p.debt or 0
                self.subscription_count = p.subscription_count or 0
                self.subscription_amount = p.subscription_amount or 0
                self.marital_status = 'Married' if p.marital_status == '신혼부부' else 'Single'
                self.kids_count = p.children_count or 0
                self.is_pregnant = getattr(p, 'is_pregnant', False)
                self.is_first_home = getattr(p, 'is_first_home', True)
                self.is_homeless = getattr(p, 'is_homeless', True)
                self.homeless_years = p.homeless_period or 0
            
            def get_marital_status_display(self):
                return "신혼부부" if self.marital_status == 'Married' else "미혼"

        return VirtualInstance(profile)

    @staticmethod
    def get_default_item(category_name, message=None):
        return {
            "top_1": {
                "title": f"조건에 부합하는 {category_name} 상품을 찾고 있습니다.",
                "name": f"{category_name} 상품 정밀 분석 중",
                "org": "청춘로 분석 엔진",
                "bank_nm": "청춘로",
                "base_rate": "-",
                "limit": "-",
                "benefit": "현재 조건에서 가입 가능한 상품을 정밀 검색 중입니다.",
                "url": "#",
                "score": 0,
                "is_default": True
            },
            "list": [],
            "reason": message or f"사용자님의 조건에 가장 근접한 {category_name} 정보를 추출 중입니다.",
            "category": category_name
        }

    @staticmethod
    def calculate_simulation(instance, collateral_value=None):
        """DSR(40%) / LTV(70%) 기반 가상 대출 한도 시뮬레이션 (단위: 만원)"""
        income = instance.total_income
        debt = instance.debt
        
        # 1. LTV 기준 한도 (주택가액의 70%)
        house_val = collateral_value or (income * 10)
        ltv_limit = int(house_val * 0.7)
        
        # 2. DSR 기준 한도 (원리금 상환액이 소득의 40% 이내)
        dsr_limit = max(0, int(income * 8) - debt)
        
        # 3. 상품 최대 한도 (일반 청년 대출 5억 상한)
        product_max = 50000
        
        calculated_limit = min(ltv_limit, dsr_limit, product_max)
        
        # 예상 금리 (소득 구간별 차등 예시)
        rate = 4.2
        if income < 3000: rate = 2.1
        elif income < 5000: rate = 3.2
        elif instance.kids_count > 0 or instance.is_pregnant: rate = 1.8 
        
        # 4. 월 예상 납입 이자 (만원 단위)
        # 공식: (대출금액 * 이자율 / 100) / 12
        monthly_interest = int((calculated_limit * rate / 100) / 12)
        
        return {
            "max_limit": calculated_limit,
            "expected_rate": rate,
            "monthly_interest": monthly_interest,
            "ltv": 70,
            "dsr": 40
        }

    @staticmethod
    def is_eligible_housing(instance, product):
        """[STRICT] 주거 상품 지능형 필터링 v17"""
        title = product.get('title', '')
        region = product.get('region', '')
        sales_price = product.get('sales_price', 0)
        income = instance.total_income
        
        # 1. PIR 기초 필터링 (가용 자본 대비 지나친 고가 매물 제외)
        if sales_price > 0:
            pir = sales_price / income
            if pir > 15: return False 
        
        # 2. 순자산 컷오프 (엄격 적용)
        net_assets = instance.assets - instance.debt
        if net_assets > 37900: # 2024년 기준 자산 기준
            if any(term in title for term in ["국민임대", "행복주택", "영구임대", "공공분양", "LH", "SH"]): 
                return False
        
        # 3. 지역 일치 여부 (핵심 필터)
        target_keyword = MatchingEngine.REGION_KEYWORD_MAP.get(instance.region, '')
        product_region = product.get('region', '')
        
        if target_keyword and target_keyword not in product_region: 
            return False
            
        # [v20] 세부 지역(시/군/구) 정밀 필터링
        if instance.sub_region:
            prod_title = title or ""
            prod_region = product.get('region') or ""
            # 공고의 지역명이나 제목에 세부 지역명이 포함되어 있는지 확인
            if instance.sub_region not in prod_region and instance.sub_region not in prod_title:
                # 만약 공고가 해당 '도' 전체 대상이 아니라 특정 '시' 대상인 경우 필터링
                if any(city in prod_region for city in MatchingEngine.REGION_KEYWORD_MAP.values() if city != target_keyword):
                    return False
            
        # [v22] 럭셔리 브랜드 필터링 (가격 정보가 누락된 경우에도 대응)
        luxury_keywords = ["라클라체", "자이드파인", "르엘", "오티에르", "디에이치", "원베일리", "아크로", "펜트하우스"]
        prod_title = product.get('title', "") or ""
        if instance.total_income < 7000 and any(lux in prod_title for lux in luxury_keywords):
            return False

        # 4. 모집 기간 필터링 (Strict - 과거 공고 배제)
        today = date.today()
        end_date = product.get('end_date')
        notice_date = product.get('notice_date')
        
        # 날짜 정보가 아예 없는 유령 데이터/과거 시장 데이터 배제
        if not end_date and not notice_date:
            return False
            
        if end_date and end_date < today:
            return False
        
        # [v25] 모집 종료일이 없는 경우 공고일 기준 60일 초과 데이터 엄격 배제 (60 Days Cutoff)
        if not end_date and notice_date:
            is_always = any(x in (product.get('title', '') or "") for x in ["상시", "기본", "급여"])
            # 일반 공고는 60일, 상시 공고도 최소 180일 이내 공고만 인정
            limit_days = 180 if is_always else 60
            if notice_date < (today - timedelta(days=limit_days)):
                return False
            
        # 5. [v19] 무주택 및 소유 이력 필터링 (Hyper-Strict)
        # 공공임대 및 대부분의 청약은 무주택 필수
        if not instance.is_homeless:
            # 유주택자는 일반 민영 청약 외에는 배제
            if any(x in product.get('category', '') for x in ["국민", "임대", "공공"]):
                return False
        
        # 생애최초 전용 매물인데 소유 이력이 있는 경우 배제
        if "생애최초" in product.get('title', '') and not instance.is_first_home:
            return False

        # 5. [v22] 지불 가능성(Affordability) 및 소득 적격성 정밀 필터링 (Hard Exclusion)
        # LH/SH 공공임대는 소득 기준이 매우 엄격함 (일반적으로 연 5,000만원 이하)
        price = product.get('sales_price', 0)
        prod_title_lower = title.lower() if title else ""
        if instance.total_income > 6000:
            if any(x in prod_title_lower for x in ["lh", "sh", "임대", "국민임대", "영구임대", "행복주택", "공공부양", "토지임대부"]):
                return False # 고소득자는 공공 성격 매물 무조건 제외
        
        # 고가 매물 필터링 (PIR 15배 이상 또는 저소득자 10억 이상 방지)
        if instance.total_income < 7000 and price > 100000: 
            return False
            
        return True

    @staticmethod
    def analyze_housing(instance):
        """[STRICT] 주거: 현실성 검증 및 추천 로직"""
        try:
            reg_key = MatchingEngine.REGION_KEYWORD_MAP.get(instance.region, '')
            
            # 필터링 및 점수화 (사용자 지역 + 전국 공고 통합)
            # 🎯 STRICT: 모집 종료일이 오늘 이후이거나 없는 경우(미정)만 포함
            today = date.today()
            local_products = list(HousingProduct.objects.filter(
                Q(region__icontains=reg_key) | Q(region__icontains="전용") | Q(region__icontains="전국"),
                Q(end_date__gte=today) | Q(end_date__isnull=True),
                notice_date__isnull=False,
                is_active=True
            ).order_by('-notice_date')[:50])
            
            valid = []
            
            for p in local_products:
                s_price = getattr(p, 'sales_price', 0)
                if not s_price: s_price = instance.total_income * 6
                
                p_data = {
                    'title': p.title, 'org': p.org, 'region': p.region,
                    'sales_price': s_price, 
                    'end_date': p.end_date, 
                    'notice_date': p.notice_date, 
                    'url': p.url or '#', 'score': 0
                }
                
                if MatchingEngine.is_eligible_housing(instance, p_data):
                    pir = s_price / max(instance.total_income, 1)
                    score = 1000 - int(pir * 30)
                    prod_cat = p.category or ""
                    prod_title = p.title or ""
                    # [v23.2] 임대 상품(LH/SH/행복주택) 가중치 대폭 강화 (+7000)
                    if "공공" in prod_cat or any(x in prod_title for x in ["LH", "SH", "행복", "임대", "전세"]): 
                        score += 7000
                    if instance.subscription_count >= 24: score += 100
                    # [v19] 무주택 기간 가점 (최대 150점)
                    score += min(instance.homeless_years * 10, 150)
                    
                    # [v24.2] 생애최초 주택 구입자 가점 대폭 상향 (+20000)
                    if "생애최초" in prod_title and instance.is_first_home:
                        score += 20000
                    
                    # [v21] 최종 결과 구성 시에만 세션 안전을 위해 문자열 변환
                    p_data['score'] = score
                    p_data['end_date'] = p.end_date.isoformat() if p.end_date else None
                    p_data['notice_date'] = p.notice_date.isoformat() if p.notice_date else None
                    
                    valid.append(p_data)
                # else: print(f"SKIP: {p_data['title']} filtered out")
                    
            if not valid:
                return MatchingEngine.get_default_item("주거", "현재 모집 중인 적격 공고가 없습니다. 추후 공고를 기다려주세요.")

            valid.sort(key=lambda x: x['score'], reverse=True)
            top = valid[0]
            pir_val = round(top['sales_price']/max(instance.total_income, 1), 1)
            
            return { 
                "top_1": top, 
                "list": valid[1:11], 
                "reason": f"거주지({reg_key}) 및 소득 대비 현실적 주거 비용(PIR {pir_val}배)을 고려한 최적 매물입니다. (현재 모집 중)" 
            }
        except Exception as e:
            # print(f"Housing Error: {e}")
            return MatchingEngine.get_default_item("주거")

    @staticmethod
    def analyze_finance(instance):
        """[STRICT] 금융: 소득 및 상황별 적격성 무한 대조"""
        try:
            today = date.today()
            # [v25] DB 레벨에서 1차 날짜 필터링 및 최신순 정렬
            local = list(FinanceProduct.objects.filter(
                Q(end_date__gte=today) | Q(end_date__isnull=True),
                is_active=True
            ).order_by('-notice_date')[:100])
            
            valid = []
            sim = MatchingEngine.calculate_simulation(instance)
            
            for p in local:
                title = p.title or ""
                
                # [v25] 모집 기간 엄격 필터링 (과거 공고 배제)
                if p.end_date and p.end_date < today:
                    continue
                
                # [v25] 공고 기간이 명시되지 않은 경우 최근 60일 이내 공고만 인정 (60 Days Cutoff)
                if not p.end_date and p.notice_date:
                    is_always = any(x in title for x in ["상시", "기본", "급여"])
                    limit_days = 180 if is_always else 60
                    if p.notice_date < (today - timedelta(days=limit_days)):
                        continue
                if any(x in title for x in ["무주택", "디딤돌", "버팀목"]) and not instance.is_homeless:
                    continue

                score = 100
                
                # [v24] 꼼꼼한 조건 대조: 혼인 상태 불일치 시 칼같이 제외
                if "신혼부부" in title and instance.marital_status not in ['Engaged', 'Married']:
                    continue
                if "미혼" in title and instance.marital_status != 'Single':
                    continue
                
                # [v24.2] 생애최초 가산점 대폭 상향 (+20000)
                if "생애최초" in title and instance.is_first_home:
                    score += 20000
                if "청년" in title and instance.age < 35:
                    score += 300
                if (instance.kids_count > 0 or instance.is_pregnant) and "신생아" in title: 
                    score += 800
                
                # 2. 소득 기반 엄격 필터링 (Income Cross-Check)
                income = instance.total_income
                income_limit = 999999
                
                # 상품명/설명 기반 소득 커트라인 추정
                if any(x in title for x in ["버팀목", "디딤돌"]): income_limit = 6000
                elif "청년전용" in title: income_limit = 5000
                elif "신생아" in title: income_limit = 13000
                elif "신혼부부" in title: income_limit = 8500
                elif any(x in title for x in ["도약계좌", "희망적금"]): income_limit = 7500
                
                # 사용자의 소득이 상품의 자격 제한을 넘어서면 칼같이 제외
                if income > income_limit: 
                    continue
                
                # 금리 기반 점수화 (저금리 우대)
                rate = p.base_rate or 4.0
                score += int((5.0 - rate) * 100)
                
                # 시딩된 주요 정책은 파격적인 가점 부여
                product_id = p.product_id or ""
                if "FIN-YOUTH" in product_id or any(x in title for x in ["적금", "청년도약", "전세자금", "청약통장"]):
                    score += 10000 
                
                valid.append({
                    'name': p.title,
                    'bank_nm': p.bank_nm,
                    'base_rate': rate,
                    'limit': min(p.limit_amt // 10000 if p.limit_amt > 0 else 50000, sim['max_limit']),
                    'url': p.url or '#',
                    'score': score
                })
            
            if not valid: return MatchingEngine.get_default_item("금융")
            valid.sort(key=lambda x: x['score'], reverse=True)
            
            return {
                "top_1": valid[0],
                "list": valid[1:6],
                "reason": f"사용자님의 {instance.get_marital_status_display()} 상태와 소득({instance.total_income}만원)에서 최저 금리가 예상되는 상품입니다."
            }
        except Exception:
            return MatchingEngine.get_default_item("금융")

    @staticmethod
    def calculate_welfare_score(instance, policy):
        """복지 상품 정밀 스코어링 엔진 v17"""
        score = 0
        title = policy.title or ""
        target = policy.target_desc or ""
        
        # 1. 연령 적합도 (만 39세 미만 청년 기본형)
        if instance.age <= 34: score += 300
        elif instance.age <= 39: score += 100
        else: return -1 # 연령 미달 칼같이 탈락
        
        # 2. 지역 가점 (v20 정밀화)
        reg_key = MatchingEngine.REGION_KEYWORD_MAP.get(instance.region, '')
        policy_region = policy.region or ""
        if reg_key and (reg_key in policy_region or "전국" in policy_region):
            score += 500
            
        # [v20] 세부 지역(시/군/구) 보너스 가점
        if instance.sub_region and instance.sub_region in policy_region:
            score += 1000 # 해당 기초지자체 전용 정책은 아주 높은 우선순위 부여
            
        # 3. 상황적 키워드 매칭 (Strict & Negative)
        marital = instance.marital_status
        is_parent = (instance.kids_count > 0 or instance.is_pregnant)
        
        # 긍정 매칭
        if marital == 'Single' and any(x in target for x in ["미혼", "1인", "독신"]): score += 200
        if marital in ['Engaged', 'Married'] and any(x in target for x in ["신혼", "부부", "혼인"]): score += 400
        if is_parent and any(x in target for x in ["자녀", "출산", "임신", "양육"]): score += 500
        
        # 부정 매칭 (오차 차단: 기혼자에게 미혼 전용 정책 추천 방지 등)
        if marital != 'Single' and any(x in target for x in ["미혼 전용", "1인 가구 한정"]): score -= 1000
        if marital == 'Single' and "신혼부부 전용" in target: score -= 1000
        if not is_parent and "다자녀 가구" in target: score -= 500
        
        # 4. [v23.1] 청년 정책 핵심 키워드 부스터 및 소득 필터링
        policy_id = policy.policy_id or ""
        keywords = ["월세", "수당", "지원금", "도약", "임대", "행복주택", "장기전세", "세금", "감면", "혜택", "비과세"]
        
        # [v24] 꼼꼼한 소득 대조: 월세지원/수당/공공임대 등은 고소득자(80M+) 무조건 탈락
        income = instance.total_income
        title_flat = title.lower().replace(" ", "")
        if income > 6000:
            # 월세, 수당, 생활비, LH, SH, 임대 키워드가 하나라도 걸리면 탈락 (-1)
            if any(x in title_flat for x in ["월세", "수당", "생활비", "지원금", "lh", "sh", "임대", "공공"]):
                return -1 
        
        if "WEL-" in policy_id or any(x in title.lower() for x in keywords):
            # 소득이 적정 수준인 경우에만 부스터 적용
            if income <= 6000:
                score += 10000 
            else:
                score += 100 # 고소득자는 부스터 없이 기본 점수만
            
        return score

    @staticmethod
    def analyze_welfare(instance):
        """[STRICT] 복지: 스코어링 시스템 기반 최적 정책 선별"""
        try:
            reg_key = MatchingEngine.REGION_KEYWORD_MAP.get(instance.region, '')
            
            # 사용자 지역 혹은 전국 정책 통합 검색 (기타 지역일 경우 전국 공고만)
            query = Q(region__icontains="전국") | Q(region__isnull=True)
            if reg_key:
                query |= Q(region__icontains=reg_key)
            
            today = date.today()
            # [v25] DB 레벨에서 쿼리 최적화 및 날짜 필터링
            local = list(WelfareProduct.objects.filter(
                query, 
                Q(end_date__gte=today) | Q(end_date__isnull=True),
                is_active=True
            ).order_by('-notice_date')[:150])
            
            valid = []
            
            for p in local:
                # [STRICT] 모집 기간 필터링 (과거 공고 절대 배제)
                if p.end_date and p.end_date < today:
                    continue
                
                # [v25] 공고일 기준 최대 60일 초과 데이터 배제 (상시는 180일) [60/180 Days Cutoff]
                if p.notice_date:
                    is_const = any(x in (p.title or "") for x in ["상시", "기본", "급여"]) or any(x in (p.benefit_desc or "") for x in ["상시", "기본", "급여"])
                    limit_days = 180 if is_const else 60
                    if p.notice_date < (today - timedelta(days=limit_days)):
                        continue

                score = MatchingEngine.calculate_welfare_score(instance, p)
                if score < 0: continue
                
                valid.append({
                    'name': p.title,
                    'org': p.org_nm,
                    'benefit': p.benefit_desc,
                    'url': p.url or '#',
                    'score': score
                })
            
            if not valid: return MatchingEngine.get_default_item("복지")
            
            # 점수 기준 정렬
            valid.sort(key=lambda x: x['score'], reverse=True)
            
            return { 
                "top_1": valid[0], 
                "list": valid[1:11], 
                "reason": f"회원님의 생애주기({instance.get_marital_status_display()})와 연령에 가장 특화된 혜택을 1순위에 배치했습니다." 
            }
        except Exception:
            return MatchingEngine.get_default_item("복지")

    @staticmethod
    def _normalize_scores(results):
        """[v24.2] 내부 점수를 UI용 0-99% 일치도로 정규화"""
        # 필터링하여 유효한 딕셔너리만 추출
        valid_items = [r for r in results if isinstance(r, dict)]
        if not valid_items: return results
        
        scores = [r.get('score', 0) for r in valid_items]
        max_score = max(scores) if scores else 0
        min_score = min(scores) if scores else 0
        
        for r in valid_items:
            # 기본 아이템(매칭 실패)은 0% 고정
            if r.get('is_default'):
                r['score'] = 0
                continue
                
            s = r.get('score', 0)
            if max_score == min_score:
                # 점수가 모두 같을 경우 (보통 부스터가 대거 적용된 상태)
                normalized = 99 if max_score > 5000 else 85
            else:
                # 70 ~ 99 사이로 선형 사영 (부스터 점수가 워낙 커서 99%에 수렴하도록 설계)
                normalized = 70 + ((s - min_score) / (max(1, max_score - min_score))) * 29
            
            r['score'] = int(normalized)
        return results

    @classmethod
    def get_full_report(cls, instance):
        """안티그래비티 전문가 보고서 통합 출력 (v20 Premium Visual)"""
        sim = cls.calculate_simulation(instance)
        housing_data = cls.analyze_housing(instance)
        finance_data = cls.analyze_finance(instance)
        welfare_data = cls.analyze_welfare(instance)
        
        # [v24.2] 결과 점수 정규화 (0-99%)
        for section in [housing_data, finance_data, welfare_data]:
            if isinstance(section, dict) and section.get('top_1'):
                items_to_norm = [section['top_1']] + section.get('list', [])
                cls._normalize_scores(items_to_norm)

        # 📊 시각화 전용 데이터 엔진 (Radar & Donut)
        # 6축: 주거안정, 금융파워, 복지수혜, 자산안전, 청년대응, 미래성장
        radar_scores = {
            "주거": housing_data.get('top_1', {}).get('score', 50),
            "금융": finance_data.get('top_1', {}).get('score', 50),
            "복지": welfare_data.get('top_1', {}).get('score', 50),
            "안전": max(20, 100 - (instance.debt / max(instance.total_income, 1) * 10)),
            "청년": 100 if instance.age <= 34 else 60,
            "성장": min(100, (instance.total_income / 1000) * 10 + 20)
        }

        return {
            "housing": housing_data,
            "finance": finance_data,
            "welfare": welfare_data,
            "user_summary": { 
                "total_income": instance.total_income, 
                "assets": instance.assets, 
                "debt": instance.debt, 
                "age": instance.age,
                "marital_desc": instance.get_marital_status_display(),
                "kid_status": "자녀/임신" if (instance.kids_count > 0 or instance.is_pregnant) else "미해당"
            },
            "financial_simulation": sim,
            "chart_data": {
                "assets": instance.assets,
                "debt": instance.debt,
                "projected_loan": sim['max_limit'],
                "radar": radar_scores
            }
        }
