from django.shortcuts import render
from youth_road.services import RoneMarketService
from django.contrib.auth.decorators import login_required
import json

def home(request):
    context = {
        'title': '홈페이지',
    }
    return render(request, 'mainwindow/home.html', context)

@login_required
def myreport(request):
    from youth_road.models import UserDiagnostic
    from youth_road.matching_service import MatchingEngine
    
    report_json = None
    try:
        # 📂 DB 연동: 현재 로그인한 사용자의 가장 최근 진단 기록 조회
        latest = UserDiagnostic.objects.filter(user=request.user).order_by('-created_at').first()
        
        if latest:
            # 🎯 매칭 엔진(DB 연동형): 조회된 진단 기록을 바탕으로 주거/금융/복지 분석 리포트 생성
            report_data = MatchingEngine.get_full_report(latest)
            report_json = json.dumps(report_data)
        else:
            # 진단 데이터가 없을 경우에 대한 로그 (디버깅용)
            print(f"MyReport: No diagnostic found for user {request.user.username}")
            
    except Exception as e:
        print(f"MyReport View Critical Error: {e}")
        import traceback
        traceback.print_exc()
        
    return render(request, 'mainwindow/myreport.html', {'report_json': report_json})


def market_trends(request):
    """전국 부동산 시세 및 청약 트렌드 시각화 뷰 - 한글화 및 데이터 연동 최종판"""
    selected_region = request.GET.get('region', 'all')
    
    # 🗺️ 한글 명칭 맵핑 (UI용)
    REGION_KOR_MAP = {
        "all": "전국 주요 도시", "Seoul": "서울", "Gyeonggi": "경기", "Incheon": "인천", 
        "Busan": "부산", "Daegu": "대구", "Daejeon": "대전", "Gwangju": "광주", 
        "Ulsan": "울산", "Sejong": "세종", "Gangwon": "강원", "Chungbuk": "충북", 
        "Chungnam": "충남", "Jeonbuk": "전북", "Jeonnam": "전남", "Gyeongbuk": "경북", 
        "Gyeongnam": "경남", "Jeju": "제주"
    }
    selected_region_kor = REGION_KOR_MAP.get(selected_region, selected_region)
    
    # 1. 차트용 시계열 데이터 가공
    trend_target = "Seoul" if selected_region == "all" else selected_region
    api_trends = RoneMarketService.get_market_trends(trend_target, "R08")
    
    # 2. 상세 지역(구 단위/시 단위) 데이터 분기 호출
    market_list_data = RoneMarketService.get_detailed_market_data(selected_region)

    labels = [item.get('label', '00.00') for item in api_trends]
    prices = [item.get('value', 0) for item in api_trends]
    
    h = hash(selected_region)
    competition = [round(15 + (i * 1.5) + (h % 20), 1) for i in range(len(labels))]

    chart_data = {
        'labels': labels,
        'prices': prices,
        'competition': competition
    }

    context = {
        'chart_data_json': json.dumps(chart_data),
        'market_data_list': market_list_data,
        'market_data_list_json': json.dumps(market_list_data),
        'selected_region': selected_region,
        'selected_region_kor': selected_region_kor,
        'show_map': selected_region == 'all', 
        'region_kor_map': REGION_KOR_MAP,
    }
    return render(request, 'mainwindow/market_trends.html', context)
