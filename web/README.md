# 🏠 청춘로(路) - 청년 및 신혼부부 맞춤형 정책 플랫폼

청춘로는 청년과 신혼부부들이 자신에게 꼭 맞는 주거, 금융, 복지 정책을 쉽고 빠르게 찾을 수 있도록 돕는 지능형 매칭 플랫폼입니다.

## 🚀 주요 기능

- **지능형 매칭 엔진**: 사용자의 연령, 소득, 자산, 혼인 상태 등을 분석하여 최적의 정책을 점수로 산출하여 추천합니다.
- **통합 인증 시스템**: 일반 로그인은 물론 네이버 소셜 로그인과 비회원(게스트) 체험 기능을 지원합니다.
- **실시간 정책 리포트**: 17개 광역자치단체의 공공 데이터와 연동하여 최신 주거 및 복지 공고를 제공합니다.
- **전문가 상담**: 정책에 대한 궁금증을 1:1 채팅을 통해 전문가에게 직접 문의할 수 있습니다.

## 🛠️ 기술 스택

- **Backend**: Python 3.13+, Django 6.0
- **Database**: SQLite (기본), PostgreSQL 연동 가능
- **Frontend**: HTML5, Vanilla CSS, JavaScript (Rich UI/UX)
- **Data Analysis**: Pandas

## ⚙️ 설치 및 실행 방법

1. **가상 환경 구성 및 패키지 설치**
   ```bash
   uv sync
   # 또는
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **환경 변수 설정**
   `.env` 파일을 생성하고 필요한 키들을 설정합니다. (SECRET_KEY 등)

3. **데이터베이스 초기화 및 데이터 로드**
   ```bash
   python manage.py migrate
   python manage.py load_data
   ```

4. **서버 실행**
   ```bash
   python manage.py runserver
   ```

## 📂 프로젝트 구조

- `auth_mypage`: 인증, 프로필 및 마이페이지 관리
- `youth_road`: 핵심 매칭 엔진 및 정책 데이터 관리
- `mainwindow`: 메인 홈 및 통합 리포트 UI
- `support`: 공지사항, FAQ 및 1:1 상담 서비스
- `config`: 프로젝트 글로벌 설정 및 유틸리티
- `data_storage`: 정책 원천 데이터 (CSV/Excel)

---
© 2026 청춘로 팀. All rights reserved.
