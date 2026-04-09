import os
import requests
import random
import google.generativeai as genai
from dotenv import load_dotenv
from .models import Policy
from django.db.models import Q

# API 설정
load_dotenv()
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "")

if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)

# --- 폴백 데이터 (DB가 비어있을 때 사용) ---
FALLBACK_POLICIES = [
    {
        'id': 'fin-1', 'category': 'Finance', 'title': '신생아 특례 디딤돌 대출',
        'summary': '최저 1.6% 금리로 최대 5억원 지원', 'tags': ['출산가구', '저금리', '최대5억'],
        'ageMax': 50, 'incomeLimit': 13000, 'requiresKids': True
    },
    {
        'id': 'fin-2', 'category': 'Finance', 'title': '청년 버팀목 전세자금대출',
        'summary': '사회초년생을 위한 연 1.8~2.7% 저금리 전세 대출', 'tags': ['청년전용', '전세자금', '저금리'],
        'ageMax': 34, 'incomeLimit': 5000, 'maritalStatus': ['single']
    },
    {
        'id': 'fin-3', 'category': 'Finance', 'title': '신혼부부 전용 버팀목 대출',
        'summary': '신혼부부 합산 연소득 7.5천만원 이하 대상', 'tags': ['신혼부부', '전세자금', '우대금리'],
        'ageMax': 45, 'incomeLimit': 7500, 'maritalStatus': ['newly', 'expecting']
    }
]

# --- 기본 매칭 및 스코어링 엔진 ---

def calculate_score(user_data, policy):
    if not user_data: return 0
    score = 75.0
    
    age = int(user_data.get('age') or 25)
    income = int(user_data.get('income') or 3000)
    marital = user_data.get('marital') or 'single'
    
    # 1. 연령 적합도
    p_age_max = policy.get('ageMax') or 100
    if age > p_age_max: score -= 35.5
    elif 19 <= age <= 34: score += 10.5
    
    # 2. 소득 적합도
    p_income_limit = policy.get('incomeLimit') or 99999
    if income > p_income_limit: score -= 45.0
    elif income < 2400: score += 15.0
    
    # 3. 혼인 상황
    if policy.get('maritalStatus') and marital not in policy['maritalStatus']:
        score -= 20.0
        
    return max(0.0, min(100.0, score))

def get_all_policies(user_data=None):
    db_policies = list(Policy.objects.all().values())
    formatted_db = [{
        'id': f"DB_{p['id']}", 'category': p['category'], 'title': p['title'],
        'summary': p['summary'], 'ageMax': p['age_max'], 'incomeLimit': p['income_limit'],
        'maritalStatus': p['marital_status'] or [], 'url': f"/policy/{p['id']}"
    } for p in db_policies]
    
    combined = formatted_db
    if not combined:
        combined = FALLBACK_POLICIES
    
    for p in combined:
        p['score'] = calculate_score(user_data, p)
        
    return sorted(combined, key=lambda x: x['score'], reverse=True)

# --- "자체 AI" (Local Inference Engine) ---

def local_inference_engine(user_message, user_data=None):
    msg = user_message.lower()
    name = user_data.get('name', '방문자') if user_data else '방문자'
    
    category_map = {
        'Finance': ['금융', '대출', '이자', '자금', '돈', '뱅크'],
        'Housing': ['주거', '집', '아파트', '전세', '월세', '청약'],
        'Employment': ['취업', '일자리', '고용', '직장', '알바', '커리어'],
        'Welfare': ['복지', '지원금', '수당', '바우처', '혜택'],
        'Legal': ['법률', '상담', '소송', '계약', '노무'],
    }
    
    target_category = None
    for cat, keywords in category_map.items():
        if any(k in msg for k in keywords):
            target_category = cat
            break

    query = Q()
    if target_category:
        query &= Q(category=target_category)
    
    msg_keywords = msg.split()
    for k in msg_keywords[:3]:
        if len(k) > 1:
            query |= Q(title__icontains=k) | Q(summary__icontains=k)

    matched_db = Policy.objects.filter(query)
    scored_matches = []
    for p in matched_db:
        p_dict = {
            'id': p.id, 'title': p.title, 'summary': p.summary, 'category': p.category,
            'ageMax': p.age_max, 'incomeLimit': p.income_limit, 'maritalStatus': p.marital_status
        }
        p_dict['score'] = calculate_score(user_data, p_dict)
        scored_matches.append(p_dict)
    
    scored_matches = sorted(scored_matches, key=lambda x: x['score'], reverse=True)[:3]

    openers = [
        f"반갑습니다 {name}님! 분석 엔진이 **'{user_message}'** 관련 데이터를 정밀 검수했습니다. 🧐",
        f"안녕하세요 {name}님, 문의하신 내용에 대해 우리 시스템의 최신 정책 DB를 대조해 보았어요. ✨",
        f"{name}님, 현재 검색하신 키워드와 가장 일치하는 **실제 신청 가능 혜택**들을 골라왔습니다. 🚀"
    ]
    
    response = f"{random.choice(openers)}\n\n"
    if scored_matches:
        response += f"분석 결과, 현재 {name}님께 가장 이득이 될 **TOP 3 추천**입니다:\n\n"
        for i, p in enumerate(scored_matches, 1):
            response += f"{i}. **{p['title']}** (적합도 {p['score']:.1f}%)\n"
            response += f"   - 요약: {p['summary'][:60]}...\n"
    else:
        response += "현재 시스템 DB 내에서 관련 정책을 찾지 못했습니다. 😅\n\n대신 '자가진단'을 완료하시면 더 정확한 추천이 가능합니다!"

    return response

def ask_expert_ai(user_message, user_data=None):
    load_dotenv(override=True)
    current_key = os.environ.get("GOOGLE_API_KEY", "")
    if current_key:
        try:
            genai.configure(api_key=current_key)
            model = genai.GenerativeModel('gemini-flash-latest')
            prompt = f"당신은 정책 전문가입니다. 사용자 질문: '{user_message}', 프로필: {user_data}. 자연스럽게 상담해 주세요."
            response = model.generate_content(prompt)
            return response.text.strip()
        except: pass
    return local_inference_engine(user_message, user_data)

def generate_expert_report(user_data, top_matches):
    load_dotenv(override=True)
    current_key = os.environ.get("GOOGLE_API_KEY", "")
    if current_key:
        try:
            genai.configure(api_key=current_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            prompt = f"데이터 보고서 작성: {user_data}, 추천목록: {top_matches[:5]}"
            response = model.generate_content(prompt)
            return response.text.strip()
        except: pass
    
    report = f"### [자체 엔진 분석 리포트] {user_data.get('name', '사용자')}님 제언\n\n"
    for p in (top_matches or [])[:5]:
        report += f"- **{p.get('title')}** (적합 지수 {p.get('score', 0):.1f}%)\n"
    return report
