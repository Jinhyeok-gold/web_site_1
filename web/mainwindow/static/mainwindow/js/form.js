const REGIONAL_DATA = {
    'Seoul': ['강남구', '강동구', '강북구', '강서구', '관악구', '광진구', '구로구', '금천구', '노원구', '도봉구', '동대문구', '동작구', '마포구', '서대문구', '서초구', '성동구', '성북구', '송파구', '양천구', '영등포구', '용산구', '은평구', '종로구', '중구', '중랑구'],
    'Busan': ['강서구', '금정구', '기장군', '남구', '동구', '동래구', '부산진구', '북구', '사상구', '사하구', '서구', '수영구', '연제구', '영도구', '중구', '해운대구'],
    'Daegu': ['남구', '달서구', '달성군', '동구', '북구', '서구', '수성구', '중구', '군위군'],
    'Incheon': ['강화군', '계양구', '미추홀구', '남동구', '동구', '부평구', '서구', '연수구', '옹진군', '중구'],
    'Gwangju': ['광산구', '남구', '동구', '북구', '서구'],
    'Daejeon': ['대덕구', '동구', '서구', '유성구', '중구'],
    'Ulsan': ['남구', '동구', '북구', '울주군', '중구'],
    'Sejong': ['세종특별자치시'],
    'Gyeonggi': ['수원시', '성남시', '의정부시', '안양시', '부천시', '광명시', '평택시', '동두천시', '안산시', '고양시', '과천시', '구리시', '남양주시', '오산시', '시흥시', '군포시', '의왕시', '하남시', '용인시', '파주시', '이천시', '안성시', '김포시', '화성시', '광주시', '양주시', '포천시', '여주시', '연천군', '가평군', '양평군'],
    'Gangwon': ['춘천시', '원주시', '강릉시', '동해시', '태백시', '속초시', '삼척시', '홍천군', '횡성군', '영월군', '평창군', '정선군', '철원군', '화천군', '양구군', '인제군', '고성군', '양양군'],
    'Chungbuk': ['청주시', '충주시', '제천시', '보은군', '옥천군', '영동군', '증평군', '진천군', '괴산군', '음성군', '단양군'],
    'Chungnam': ['천안시', '공주시', '보령시', '아산시', '서산시', '논산시', '계룡시', '당진시', '금산군', '부여군', '서천군', '청양군', '홍성군', '예산군', '태안군'],
    'Jeonbuk': ['전주시', '군산시', '익산시', '정읍시', '남원시', '김제시', '완주군', '진안군', '무주군', '장수군', '임실군', '순창군', '고창군', '부안군'],
    'Jeonnam': ['목포시', '여수시', '순천시', '나주시', '광양시', '담양군', '곡성군', '구례군', '고흥군', '보성군', '화순군', '장흥군', '강진군', '해남군', '영암군', '무안군', '함평군', '영광군', '장성군', '완도군', '진도군', '신안군'],
    'Gyeongbuk': ['포항시', '경주시', '김천시', '안동시', '구미시', '영주시', '영천시', '상주시', '문경시', '경산시', '의성군', '청송군', '영양군', '영덕군', '청도군', '고령군', '성주군', '칠곡군', '예천군', '봉화군', '울진군', '울릉군'],
    'Gyeongnam': ['창원시', '진주시', '통영시', '사천시', '김해시', '밀양시', '거제시', '양산시', '의령군', '함안군', '창녕군', '고성군', '남해군', '하동군', '산청군', '함양군', '거창군', '합천군'],
    'Jeju': ['제주시', '서귀포시']
};

let currentUserData = null;
let currentReport = null;

function setView(viewId) {
    ['hero', 'form', 'matching', 'result'].forEach(v => {
        const el = document.getElementById('view-' + v);
        if(el) el.classList.add('hidden');
    });
    document.getElementById('view-' + viewId).classList.remove('hidden');
    window.scrollTo(0,0);
}

function nextStep(step) {
    [1, 2, 3].forEach(s => {
        const stepEl = document.getElementById('step-' + s);
        const dotEl = document.getElementById('dot-' + s);
        if(stepEl) stepEl.classList.remove('active');
        if(dotEl) dotEl.classList.remove('active');
    });
    const targetStep = document.getElementById('step-' + step);
    const targetDot = document.getElementById('dot-' + step);
    if(targetStep) targetStep.classList.add('active');
    if(targetDot) targetDot.classList.add('active');
}

function updateSubRegions() {
    const region = document.getElementById('inp-region').value;
    const subSelect = document.getElementById('inp-sub-region');
    subSelect.innerHTML = '<option value="">세부 지역 선택</option>';
    
    if(REGIONAL_DATA[region]) {
        REGIONAL_DATA[region].forEach(sub => {
            const opt = document.createElement('option');
            opt.value = sub;
            opt.textContent = sub;
            subSelect.appendChild(opt);
        });
    }
}

async function handleMatch() {
    setView('matching');
    
    const userData = {
        age: parseInt(document.getElementById('inp-age').value),
        region: document.getElementById('inp-region').value,
        sub_region: document.getElementById('inp-sub-region').value,
        is_homeless: document.getElementById('inp-is-homeless').checked,
        income: parseInt(document.getElementById('inp-income').value),
        assets: parseInt(document.getElementById('inp-assets').value),
        debt: parseInt(document.getElementById('inp-debt').value),
        marital: document.getElementById('inp-marital').value,
        kids: parseInt(document.getElementById('inp-kids').value),
        sub_count: parseInt(document.getElementById('inp-subscription').value),
        first_home: document.getElementById('inp-is-first-home').checked,
        low_income: false // Removed from UI, default false
    };
    currentUserData = userData;

    try {
        const res = await fetch('/chatbot/api/policies/', {
            method: 'POST',
            headers: {'Content-Type': 'application/json', 'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || ''},
            body: JSON.stringify({ user_data: userData })
        });
        
        const contentType = res.headers.get("content-type");
        if (!contentType || !contentType.includes("application/json")) {
            const errorText = await res.text();
            console.error("Non-JSON response received:", errorText);
            throw new Error("서버 엔진 내부 오류가 발생했습니다. (HTTP " + res.status + ")");
        }
        
        const data = await res.json();
        if (data.error) {
            throw new Error(data.error);
        }
        currentReport = data.report;
        
        renderResults();
        await fetchAIReport(userData, data.report);
        setView('result');
    } catch(e) {
        console.error("DEBUG [handleMatch Error]:", e);
        setView('form');
        alert("분석 엔진 연결 중 오류가 발생했습니다: " + e.message);
    }
}

function renderResults() {
    if(!currentReport) return;
    
    const container = document.getElementById('matching-results-container');
    const { housing, finance, welfare, chart_data, financial_simulation } = currentReport;
    
    let html = '';
    
    // Category 1: Housing
    html += `<div class="category-section">
        <h3 class="category-title">🏠 맞춤형 주거 정책</h3>
        <p class="category-reason">${housing.reason}</p>
        <div class="result-cards-row">
            ${renderPolicyCard(housing.top_1, 'Housing', true)}
            ${housing.list.slice(0, 2).map(p => renderPolicyCard(p, 'Housing')).join('')}
        </div>
    </div>`;

    // Category 2: Finance
    html += `<div class="category-section">
        <h3 class="category-title">💰 금융 및 대출 지원</h3>
        <p class="category-reason">${finance.reason}</p>
        <div class="result-cards-row">
            ${renderPolicyCard(finance.top_1, 'Finance', true)}
            ${finance.list.slice(0, 2).map(p => renderPolicyCard(p, 'Finance')).join('')}
        </div>
    </div>`;

    // Category 3: Welfare
    html += `<div class="category-section">
        <h3 class="category-title">🎁 맞춤 복지 및 혜택</h3>
        <p class="category-reason">${welfare.reason}</p>
        <div class="result-cards-row">
            ${renderPolicyCard(welfare.top_1, 'Welfare', true)}
            ${welfare.list.slice(0, 2).map(p => renderPolicyCard(p, 'Welfare')).join('')}
        </div>
    </div>`;

    container.innerHTML = html;
    
    renderVisuals(chart_data, financial_simulation);
}

function renderPolicyCard(p, type, isTop = false) {
    if(!p) return '';
    const score = p.score ? p.score : 85; 
    const officialUrl = (p.url && p.url !== '#') ? p.url : 'https://www.youthcenter.go.kr';
    
    return `
        <div class="policy-card-modern ${isTop ? 'top-match' : ''}">
            <div class="card-badge">${isTop ? '1순위' : '추천'}</div>
            <div class="card-score">${score}% 일치</div>
            <h4>${p.title || p.name}</h4>
            <div class="card-info">
                <span class="org-name">${p.org || p.bank_nm || '청년정책 거버넌스'}</span>
                ${p.base_rate ? `<span class="rate">연 ${p.base_rate}%~</span>` : ''}
            </div>
            <p class="card-summary">${p.summary || p.benefit || '청년들의 주거/금융 안정을 위해 마련된 맞춤형 정책입니다.'}</p>
            <div class="card-footer">
                <a href="${officialUrl}" target="_blank" rel="noopener noreferrer" class="card-link">
                    공고 확인하기 <i class="fas fa-external-link-alt"></i>
                </a>
            </div>
        </div>
    `;
}

function renderVisuals(chart_data, sim) {
    const visualPanel = document.getElementById('visual-analytics-panel');
    const radar = chart_data.radar;
    
    visualPanel.innerHTML = `
        <div class="visual-grid">
            <div class="radar-box">
                <h4>📊 정책 수혜 밸런스</h4>
                <div class="radar-chart-simple">
                    ${Object.entries(radar).map(([key, val]) => `
                        <div class="radar-bar-container">
                            <span class="radar-label">${key}</span>
                            <div class="radar-bar-bg">
                                <div class="radar-bar-fill" style="width: ${val}%"></div>
                            </div>
                            <span class="radar-val">${Math.round(val)}%</span>
                        </div>
                    `).join('')}
                </div>
            </div>
            <div class="sim-box">
                <h4>🏦 대출 시뮬레이션</h4>
                <div class="sim-content">
                    <div class="sim-item">
                        <span>예상 한도</span>
                        <strong>${sim.max_limit.toLocaleString()}만원</strong>
                    </div>
                    <div class="sim-item">
                        <span>예상 금리</span>
                        <strong>연 ${sim.expected_rate}%</strong>
                    </div>
                    <div class="sim-item">
                        <span>월 납입액</span>
                        <strong>약 ${sim.monthly_interest.toLocaleString()}만원</strong>
                    </div>
                </div>
                <div class="pir-gauge">
                    <div class="pir-fill" style="width: ${sim.dsr}%"></div>
                    <span class="pir-text">DSR 건전성 ${sim.dsr}%</span>
                </div>
                <!-- AI 분석 텍스트가 들어갈 자리 -->
                <div id="ai-report-content" class="report-text" style="margin-top: 25px;"></div>
            </div>
        </div>
    `;
}

async function fetchAIReport(userData, reportData) {
    const box = document.getElementById('ai-report-content');
    box.innerHTML = '<div class="loader-circle mini"></div> 보고서를 작성 중입니다...';
    try {
        const res = await fetch('/chatbot/api/ai-report/', {
            method: 'POST',
            headers: {'Content-Type': 'application/json', 'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || ''},
            body: JSON.stringify({ user_data: userData, report_data: reportData })
        });
        const data = await res.json();
        box.innerHTML = `<div class="report-wrapper"><p class="report-paragraph">${data.report.replace(/\n/g, '<br/>')}</p></div>`;
    } catch(e) { 
        box.innerText = "보고서 생성 중 오류가 발생했습니다. 아래 맞춤 목록을 확인해 주세요."; 
    }
}

// 초기화
document.addEventListener('DOMContentLoaded', () => {
    console.log("Form Wizard Monitoring System Initialized.");
    if (document.getElementById('inp-region')) {
        updateSubRegions();
    }
});

// Chatbot 모듈
function toggleChatbot() { document.getElementById('chatbot-modal').classList.toggle('hidden'); }
async function handleChatSubmit(e) {
    e.preventDefault();
    const input = document.getElementById('chat-input');
    const msg = input.value.trim();
    if(!msg) return;

    appendChat('user', msg);
    input.value = '';

    try {
        const response = await fetch('/chatbot/api/chat/', {
            method: 'POST',
            headers: {'Content-Type': 'application/json', 'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value},
            body: JSON.stringify({ message: msg, user_data: currentUserData })
        });
        const data = await response.json();
        appendChat('bot', data.reply);
    } catch(e) {
        appendChat('bot', "오류가 발생했습니다.");
    }
}
function appendChat(role, text) {
    const box = document.getElementById('chat-messages');
    const div = document.createElement('div');
    div.className = `chat-bubble chat-${role}`;
    div.innerHTML = text.replace(/\n/g, '<br/>');
    box.appendChild(div);
    box.scrollTop = box.scrollHeight;
}