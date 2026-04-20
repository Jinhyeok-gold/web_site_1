from .matching_service import MatchingEngine
from auth_mypage.models import UserProfile
from .models import UserDiagnostic

def global_matching_results(request):
    """
    모든 페이지에서 실시간 매칭 결과를 사용할 수 있도록 제공하는 컨텍스트 프로세서
    로그인한 사용자의 UserProfile 정보를 바탕으로 MatchingEngine 호출
    """
    context = {
        'side_matching_results': None
    }
    
    if request.user.is_authenticated:
        try:
            # 1. auth_mypage의 UserProfile 가져오기
            profile = UserProfile.objects.filter(user=request.user).first()
            virtual_instance = None
            
            if profile and profile.sido:
                # UserProfile 정보를 MatchingEngine용 가상 인스턴스로 변환
                virtual_instance = MatchingEngine.map_profile_to_instance(profile)
            else:
                # 2. [Fallback] UserProfile이 없거나 지역 정보가 없으면 최신 UserDiagnostic 검색
                diag = UserDiagnostic.objects.filter(user=request.user).order_by('-created_at').first()
                if diag:
                    # UserDiagnostic은 이미 MatchingEngine과 호환되는 필드 구조를 가짐
                    virtual_instance = diag
            
            if virtual_instance:
                # 전체 리포트 생성
                report = MatchingEngine.get_full_report(virtual_instance)
                
                # 모든 매칭 상품들을 리스트로 정리
                def get_all_items(section_data):
                    if not section_data: return []
                    items = []
                    if section_data.get('top_1'):
                        items.append(section_data['top_1'])
                    items.extend(section_data.get('list', []))
                    return items

                context['side_matching_results'] = {
                    'housing_list': get_all_items(report.get('housing')),
                    'finance_list': get_all_items(report.get('finance')),
                    'welfare_list': get_all_items(report.get('welfare')),
                    'user_name': request.user.last_name or request.user.username
                }
        except Exception as e:
            # 에러 발생 시 로그를 남기거나 빈 결과를 전달하여 페이지 중단 방지
            print(f"Global Matching Context Error: {e}")
            pass
            
    return context

def real_estate_market_ticker(request):
    """실시간 부동산 시장 지수를 전역 컨텍스트로 제공 - 2026년 4월 '억' 단위 고정"""
    from .services import RoneMarketService
    
    # R-ONE API를 사용하여 실제 시세 데이터 가져오기 시도
    ticker_data = RoneMarketService.get_ticker_data()
    
    if not ticker_data:
        # API 실패 시에도 사용자가 원하는 2026년 4월 기준 '억' 단위 최신 시뮬레이션 데이터 제공
        ticker_data = [
            {'name': '서울', 'price': '12.4억', 'trend': 0.12, 'is_up': True},
            {'name': '경기', 'price': '7.2억', 'trend': 0.08, 'is_up': True},
            {'name': '인천', 'price': '4.5억', 'trend': 0.05, 'is_up': False},
            {'name': '세종', 'price': '6.1억', 'trend': 0.21, 'is_up': True},
            {'name': '부산', 'price': '5.3억', 'trend': 0.03, 'is_up': True},
            {'name': '대구', 'price': '4.1억', 'trend': 0.02, 'is_up': False},
            {'name': '대전', 'price': '3.8억', 'trend': 0.07, 'is_up': True},
            {'name': '광주', 'price': '3.2억', 'trend': 0.04, 'is_up': True},
        ]
    
    return {
        'real_estate_ticker': ticker_data
    }
