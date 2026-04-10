# 청춘로(路) - AI 지능형 정책 매칭 챗봇

청년 주거·금융 정책을 AI가 분석하여 맞춤형 정책을 추천해주는 챗봇 시스템입니다.

---

## 🚀 빠른 시작 (설치 & 실행)

### 1단계: Python 설치 확인
```bash
python --version  # Python 3.10 이상 필요
```

### 2단계: 패키지 설치
```bash
pip install -r requirements.txt
```

### 3단계: 환경 변수 설정
`.env.example` 파일을 복사하여 `.env` 파일을 만들고 값을 입력하세요.
```bash
# Windows
copy chatbot\.env.example .env

# .env 파일 내용 예시
SECRET_KEY=your-secret-key-here
GOOGLE_API_KEY=your-gemini-api-key-here
DEBUG=True
```

> **GOOGLE_API_KEY 발급**: https://aistudio.google.com → Get API key → Create API key

### 4단계: DB 초기화
```bash
python manage.py migrate
```

### 5단계: 서버 실행
```bash
python manage.py runserver
```

### 6단계: 접속
브라우저에서 → **http://localhost:8000**

---

## 📁 프로젝트 구조

```
miniproject-main/
├── chatbot/          ← AI 챗봇 앱 (핵심)
│   ├── core/
│   │   ├── views.py      ← 챗봇 API 엔드포인트
│   │   ├── services.py   ← Gemini LLM 연동 & 로컬 AI 엔진
│   │   └── models.py     ← 사용자 프로필 모델
│   └── templates/
│       └── index.html    ← 챗봇 SPA 메인 화면
├── config/           ← Django 설정
├── data_storage/     ← 정책 CSV 데이터
├── static/           ← CSS/JS 자원
├── templates/        ← 공통 HTML 템플릿
│   ├── base.html         ← 챗봇 UI & 네비게이션 포함
│   └── result.html       ← AI 분석 리포트 페이지
├── youth_road/       ← 정책 매칭 엔진 앱
├── manage.py         ← Django 서버 실행 파일
├── requirements.txt  ← 필요 패키지 목록
└── .env              ← 환경 변수 (별도 전달)
```

---

## 🤖 챗봇 동작 방식

1. 우측 하단 **[상담]** 버튼 클릭
2. 질문 입력 (예: "전세자금대출 조건이 뭐야?")
3. AI가 사용자 프로필 기반으로 맞춤 답변 제공
4. 정책 버튼 클릭 → **실제 정부 사이트로 이동**

### AI 엔진 구조
```
Gemini API (LLM) → 실패 시 → 로컬 지능형 엔진 (자동 대체)
```
API 키가 없거나 한도 초과 시 로컬 엔진이 자동으로 작동합니다.

---

## ⚙️ 주요 기능

- ✅ AI 정책 매칭 (소득·나이·지역 기반)
- ✅ 실시간 챗봇 상담 (Gemini LLM)
- ✅ 정책 사이트 직접 연결 버튼
- ✅ 대화 이력 유지 (세션 기반)
- ✅ 사용자 프로필 관리
- ✅ AI 분석 리포트 (레이더 차트)

---

## 🔑 환경 변수 설명

| 변수명 | 설명 | 필수 |
|---|---|---|
| `SECRET_KEY` | Django 보안 키 | ✅ |
| `GOOGLE_API_KEY` | Gemini AI API 키 | 선택 (없으면 로컬 엔진 사용) |
| `DEBUG` | 개발 모드 (True/False) | ✅ |
| `DATABASE_URL` | DB 주소 (기본: SQLite) | 선택 |
