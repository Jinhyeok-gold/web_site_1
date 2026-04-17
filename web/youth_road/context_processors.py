from .matching_service import MatchingEngine
from auth_mypage.models import UserProfile

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
            # auth_mypage의 UserProfile 가져오기
            profile = UserProfile.objects.filter(user=request.user).first()
            if profile:
                # MatchingEngine용 가상 인스턴스로 변환
                virtual_instance = MatchingEngine.map_profile_to_instance(profile)
                
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
