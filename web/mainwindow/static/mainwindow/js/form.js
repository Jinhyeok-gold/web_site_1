/* global Chart */
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
let activeCharts = {
    gauge: null,
    radar: null
};

function setView(viewId) {
  const doSwitch = () => {
    ['hero','matching','result','recap'].forEach(v => {
      document.getElementById(`view-${v}`)?.classList.add('hidden');
    });
    document.getElementById(`view-${viewId}`)?.classList.remove('hidden');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  if (!document.startViewTransition) { doSwitch(); return; }
  document.startViewTransition(doSwitch);
}

function nextStep(step, dir = 'forward') {
  const doSwitch = () => {
    [1, 2, 3].forEach(s => {
      document.getElementById(`step-${s}`)?.classList.remove('active');
      document.getElementById(`dot-${s}`)?.classList.remove('active');
    });
    document.getElementById(`step-${step}`)?.classList.add('active');
    document.getElementById(`dot-${step}`)?.classList.add('active');

    const fill = document.getElementById('progress-fill');
    if (fill) fill.style.width = (step / 3 * 100) + '%';

    document.querySelector('.form-panel')
      ?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  };

  // View Transitions 지원 여부 체크 → 폴백 안전
  if (!document.startViewTransition) { doSwitch(); return; }

  // 방향 힌트를 data 속성으로 넘겨 CSS가 읽을 수 있게
  document.documentElement.dataset.vtDir = dir;
  document.startViewTransition(doSwitch);
}

function updateSubRegions() {
    const region = document.getElementById('inp-region').value;
    const subSelect = document.getElementById('inp-sub-region');
    subSelect.innerHTML = '<option value="" selected disabled hidden></option>';
    
    if(REGIONAL_DATA[region]) {
        REGIONAL_DATA[region].forEach(sub => {
            const opt = document.createElement('option');
            opt.value = sub;
            opt.textContent = sub;
            subSelect.appendChild(opt);
        });
    }
    
    // Manually trigger has-value check for sub-region
    if(window.updateHasValue) {
        window.updateHasValue(subSelect);
    }
}

async function handleMatch() {
    console.log("Starting precision diagnostic matching...");
    setView('matching');
    
    // [STABILITY] Helper for safe data collection
    const getVal = (id, fallback = 0) => {
        const el = document.getElementById(id);
        if(!el) {
            console.warn(`[MISSING FIELD] ${id} was not found in the document.`);
            return fallback;
        }
        return el.value;
    };

    const getChecked = (id) => {
        const el = document.getElementById(id);
        if(!el) {
            console.warn(`[MISSING CHECKBOX] ${id} was not found.`);
            return false;
        }
        return el.checked;
    };

    // Collect all detailed fields
    const userData = {
        age: parseInt(getVal('inp-age', 29)),
        region: getVal('inp-region', 'Seoul'),
        sub_region: getVal('inp-sub-region', ''),
        is_homeless: getChecked('inp-is-homeless'),
        income: parseInt(getVal('inp-income', 3000)),
        assets: parseInt(getVal('inp-assets', 5000)),
        debt: parseInt(getVal('inp-debt', 0)),
        marital: getVal('inp-marital', 'Single'),
        kids: parseInt(getVal('inp-kids', 0)),
        sub_count: parseInt(getVal('inp-subscription', 24)),
        sub_amount: parseInt(getVal('inp-subscription-amount', 240)),
        homeless_years: parseInt(getVal('inp-homeless-years', 0)),
        is_pregnant: getChecked('inp-is-pregnant'),
        first_home: getChecked('inp-is-first-home'),
        low_income: false
    };
    currentUserData = userData;
    console.log("Diagnostic Data Collected:", userData);

    try {
        const res = await fetch('/chatbot/api/policies/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json', 
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || ''
            },
            body: JSON.stringify({ user_data: userData })
        });
        
        if (!res.ok) {
            const errorText = await res.text();
            console.error("API Error Response:", errorText);
            throw new Error(`분석 중 오류 발생 (상태코드: ${res.status})`);
        }
        
        const data = await res.json();
        console.log("Matching Engine Results Received:", data);
        if (data.error) throw new Error(data.error);
        
        currentReport = data.report;
        
        // Reset container and render
        const container = document.getElementById('matching-results-container');
        if (container) container.innerHTML = ""; 
        
        renderResults();
        await fetchAIReport(userData, data.report);
        currentReport = data.report;
        renderRecap(data.report);
    } catch(e) {
        console.error("Match Error Trace:", e);
        setView('hero');
        alert("분석 엔진 연결 실패: " + e.message);
    }
}

function renderResults() {
    if(!currentReport) return;
    
    const container = document.getElementById('matching-results-container');
    const { 
        housing = { list: [], reason: "" }, 
        finance = { list: [], reason: "" }, 
        welfare = { list: [], reason: "" },
        chart_data = { radar: {} },
        financial_simulation = { max_limit: 0, monthly_interest: 0 }
    } = currentReport;
    
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
    const radarData = chart_data.radar;
    const matchingScore = Math.round((radarData["주거"] + radarData["금융"] + radarData["복지"]) / 3);

    // 1. Overall Matching Gauge (Doughnut)
    const gaugeCtx = document.getElementById('scoreGaugeCanvas').getContext('2d');
    
    // [STABILITY] Destroy existing chart instance
    if (activeCharts.gauge) activeCharts.gauge.destroy();
    
    activeCharts.gauge = new Chart(gaugeCtx, {
        type: 'doughnut',
        data: {
            datasets: [{
                data: [matchingScore, 100 - matchingScore],
                backgroundColor: ['#6366f1', '#f1f5f9'],
                borderWidth: 0,
                circumference: 270,
                rotation: 225,
                cutout: '85%',
                borderRadius: 10
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { tooltip: { enabled: false }, legend: { display: false } },
            animation: { duration: 2000, easing: 'easeOutQuart' }
        }
    });
    
    // Animate the score number
    animateNumber('gauge-score-val', 0, matchingScore, 2000);

    // 2. Financial Simulation Restore
    const simLimitEl = document.getElementById('sim-limit-val');
    const simInterestEl = document.getElementById('sim-interest-val');
    if (simLimitEl && sim) {
        animateNumber('sim-limit-val', 0, sim.max_limit, 1500);
    }
    if (simInterestEl && sim) {
        animateNumber('sim-interest-val', 0, sim.monthly_interest, 1500);
    }

    // 3. Policy Suitability Radar Chart
    const radarCtx = document.getElementById('radarChartCanvas').getContext('2d');
    
    // [STABILITY] Destroy existing chart instance
    if (activeCharts.radar) activeCharts.radar.destroy();
    
    activeCharts.radar = new Chart(radarCtx, {
        type: 'radar',
        data: {
            labels: Object.keys(radarData),
            datasets: [{
                label: '추천 적합도',
                data: Object.values(radarData),
                backgroundColor: 'rgba(99, 102, 241, 0.2)',
                borderColor: '#6366f1',
                pointBackgroundColor: '#6366f1',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                r: {
                    beginAtZero: true,
                    max: 100,
                    ticks: { display: false },
                    grid: { color: '#f1f5f9' },
                    pointLabels: { font: { size: 12, weight: 'bold' } }
                }
            },
            plugins: { legend: { display: false } }
        }
    });
}

function animateNumber(id, start, end, duration) {
    const obj = document.getElementById(id);
    let startTimestamp = null;
    const step = (timestamp) => {
        if (!startTimestamp) startTimestamp = timestamp;
        const progress = Math.min((timestamp - startTimestamp) / duration, 1);
        obj.innerHTML = Math.floor(progress * (end - start) + start);
        if (progress < 1) {
            window.requestAnimationFrame(step);
        }
    };
    window.requestAnimationFrame(step);
}

async function fetchAIReport(userData, reportData) {
    const box = document.getElementById('ai-report-content');
    try {
        const res = await fetch('/chatbot/api/ai-report/', {
            method: 'POST',
            headers: {'Content-Type': 'application/json', 'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || ''},
            body: JSON.stringify({ user_data: userData, report_data: reportData })
        });
        const data = await res.json();
        // Modernized text injection
        box.innerHTML = `<div class="report-wrapper fade-in">
            <div class="ai-avatar"><i class="fas fa-robot"></i> Expert Analyst</div>
            <p class="report-paragraph">${data.report.replace(/\n/g, '<br/>')}</p>
        </div>`;
    } catch(e) { 
        box.innerHTML = "리포트를 가져오는데 실패했습니다. 아래 상세 목록을 확인해주세요."; 
    }
}

async function sendEmailToUser() {
    console.log("Attempting to send report via email...");
    const btn = document.querySelector('.btn-email-user');
    const originalHtml = btn.innerHTML;
    
    try {
        btn.disabled = true;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 전송 중...';
        
        const res = await fetch('/chatbot/api/send-email/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || ''
            }
        });
        
        const data = await res.json();
        if (data.status === 'success') {
            alert("📩 " + data.message);
            btn.innerHTML = '<i class="fas fa-check"></i> 전송 완료';
            btn.style.background = '#059669';
        } else {
            throw new Error(data.error);
        }
    } catch(e) {
        console.error("Email send failed:", e);
        alert("이메일 전송 실패: " + e.message);
        btn.innerHTML = originalHtml;
        btn.disabled = false;
    }
}

// 초기화
document.addEventListener('DOMContentLoaded', () => {
    console.log("Form Wizard Monitoring System Initialized.");
    
    // Floating labels helper: Add 'has-value' class when input/select is not empty
    const inputs = document.querySelectorAll('.form-input, .form-select');
    window.updateHasValue = (el) => {
        if (el.value && el.value !== "") {
            el.classList.add('has-value');
        } else {
            el.classList.remove('has-value');
        }
    };

    inputs.forEach(el => {
        // Initial check
        window.updateHasValue(el);
        
        // Listener for changes
        el.addEventListener('input', () => window.updateHasValue(el));
        el.addEventListener('change', () => window.updateHasValue(el));
        // Add focus/blur listeners for extra reactivity
        el.addEventListener('focus', () => el.classList.add('is-focused'));
        el.addEventListener('blur', () => el.classList.remove('is-focused'));
    });

    if (document.getElementById('inp-region')) {
        updateSubRegions();
    }
});

// Chatbot 모듈 [v22 Advanced Integration]
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
            body: JSON.stringify({ message: msg, user_data: currentUserData, report_data: currentReport })
        });
        const data = await response.json();
        
        let text = data.reply;
        
        // 🎯 [ID:...] 태그 모두 찾기 (지원: 중복 카드)
        const idMatches = [...text.matchAll(/\[ID:([\w-]+)\]/g)];
        
        // 태그들을 제거한 본문 텍스트 추출
        let cleanText = text;
        idMatches.forEach(m => { cleanText = cleanText.replace(m[0], ''); });
        
        // 본문 먼저 출력
        appendChat('bot', cleanText.trim());
        
        // 발견된 모든 상품 카드 순차적으로 렌더링
        for (const match of idMatches) {
            await appendProductCardToChat(match[1]);
        }
    } catch(e) {
        appendChat('bot', "오류가 발생했습니다. 잠시 후 다시 시도해주세요.");
    }
}

async function appendProductCardToChat(productId) {
    const box = document.getElementById('chat-messages');
    
    // 로딩 인디케이터
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'chat-bubble chat-bot loading-card';
    loadingDiv.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 맞춤 정책 정보를 불러오는 중...';
    box.appendChild(loadingDiv);
    box.scrollTop = box.scrollHeight;

    try {
        const res = await fetch(`/chatbot/api/product-detail/?id=${productId}`);
        const data = await res.json();
        if(loadingDiv.parentNode) box.removeChild(loadingDiv);
        
        if (data.error) throw new Error(data.error);

        const cardDiv = document.createElement('div');
        cardDiv.className = 'chat-product-card fade-in';
        cardDiv.innerHTML = `
            <div class="chat-card-header">
                <span class="chat-card-type">${data.type === 'FinanceProduct' ? '금융' : '주거'}</span>
                <strong>${data.title}</strong>
            </div>
            <p class="chat-card-summary">${data.summary.substring(0, 100)}...</p>
            <a href="${data.url}" target="_blank" class="chat-card-btn">상세보기 <i class="fas fa-external-link-alt"></i></a>
        `;
        box.appendChild(cardDiv);
    } catch (e) {
        if(loadingDiv.parentNode) box.removeChild(loadingDiv);
        // 에러 시 로그만 남기고 지나감 (이미 본문이 출력되었으므로)
        console.warn("Card render failed for ID:", productId);
    }
    box.scrollTop = box.scrollHeight;
}

function appendChat(role, text) {
    if(!text) return;
    const box = document.getElementById('chat-messages');
    const div = document.createElement('div');
    div.className = `chat-bubble chat-${role}`;
    
    // [[BUTTON:TYPE|LABEL]] 모두 처리
    let cleanText = text;
    const btnMatches = [...text.matchAll(/\[\[BUTTON:([\w_]+)\|([^\]]+)\]\]/g)];
    let buttonsHtml = '';
    
    if (btnMatches.length > 0) {
        buttonsHtml = '<div class="chat-btn-row">';
        btnMatches.forEach(m => {
            cleanText = cleanText.replace(m[0], '');
            buttonsHtml += `<button class="chat-action-btn" onclick="handleChatAction('${m[1]}')">${m[2]}</button>`;
        });
        buttonsHtml += '</div>';
    }

    div.innerHTML = cleanText.replace(/\n/g, '<br/>') + buttonsHtml;
    box.appendChild(div);
    box.scrollTop = box.scrollHeight;
}

function handleChatAction(type) {
    if (type === 'REPORT_VIEW') setView('result');
    else if (type === 'POLICY_LIST') window.location.href = 'https://www.youthcenter.go.kr';
    else if (type === 'DSR_CALC') alert('DSR 계산기 기능을 준비 중입니다.');
    else toggleChatbot();
}
