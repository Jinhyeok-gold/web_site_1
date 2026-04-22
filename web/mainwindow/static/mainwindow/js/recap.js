/* ==========================================================================
   recap.js — 딱맞춤 진단 결과 Recap 슬라이드
   form.js 하단에 추가하거나 별도 <script src>로 로드
   의존성: Chart.js (base.html에서 이미 로드됨)
   ========================================================================== */

const Recap = (() => {

    /* ── 상태 ── */
    let cur = 0;
    let busy = false;
    let radarDrawn = false;
    const TOTAL = 6;

    /* ── DOM 캐시 ── */
    const shell   = () => document.getElementById('recap-shell');
    const progEl  = () => document.getElementById('recap-prog');
    const prevBtn = () => document.getElementById('recap-btn-prev');
    const nextBtn = () => document.getElementById('recap-btn-next');
    const cards   = () => [...document.querySelectorAll('.recap-card')];
    const dots    = () => [...document.querySelectorAll('.recap-dot')];

    /* ── UI 동기화 ── */
    function syncUI() {
        dots().forEach((d, i) => d.classList.toggle('on', i === cur));
        progEl().style.width = ((cur + 1) / TOTAL * 100) + '%';
        prevBtn().style.visibility = cur === 0 ? 'hidden' : 'visible';

        // 마이리포트 모달 안인지 홈 리캡인지 구분
        const isModal = !!document.getElementById('recap-modal') &&
                        !document.getElementById('recap-modal').classList.contains('hidden');
        nextBtn().textContent = cur === TOTAL - 1
            ? (isModal ? '마이리포트로 돌아가기' : '전체 리포트 보기 →')
            : '다음 →';
    }

    /* ── 카드 1: 숫자 카운트업 ── */
    function animScore(targetScore) {
        let v = 0;
        const el = document.getElementById('recap-score-num');
        if (!el) return;
        const iv = setInterval(() => {
            v = Math.min(v + 2, targetScore);
            el.innerHTML = v + '<sub>%</sub>';
            if (v >= targetScore) clearInterval(iv);
        }, 16);
    }

    /* ── 카드 2: 레이더 차트 드로우 ── */
    function drawRadar(radarData) {
        if (radarDrawn) return;
        radarDrawn = true;

        // 바 차트 채우기
        document.querySelectorAll('.rc2-stat-fill').forEach(b => {
            b.style.width = b.dataset.w + '%';
        });

        const ctx = document.getElementById('recap-radar');
        if (!ctx) return;

        const labels = Object.keys(radarData);
        const values = Object.values(radarData);
        const chart = new Chart(ctx.getContext('2d'), {
            type: 'radar',
            data: {
                labels,
                datasets: [{
                    data: labels.map(() => 0),
                    backgroundColor: 'rgba(255,255,255,.2)',
                    borderColor: 'rgba(255,255,255,.95)',
                    pointBackgroundColor: '#fff',
                    pointBorderColor: 'transparent',
                    pointRadius: 5,
                    borderWidth: 2.5
                }]
            },
            options: {
                responsive: false,
                animation: false,
                plugins: { legend: { display: false }, tooltip: { enabled: false } },
                scales: {
                    r: {
                        beginAtZero: true, max: 100,
                        ticks: { display: false },
                        grid: { color: 'rgba(255,255,255,.22)' },
                        angleLines: { color: 'rgba(255,255,255,.22)' },
                        pointLabels: { color: 'rgba(255,255,255,.9)', font: { size: 12, weight: '600' } }
                    }
                }
            }
        });

        // ease-out 드로우 애니메이션
        let f = 0;
        const tf = 60;
        (function step() {
            f++;
            const p = 1 - Math.pow(1 - f / tf, 3);
            chart.data.datasets[0].data = values.map(v => Math.round(v * p));
            chart.update('none');
            if (f < tf) requestAnimationFrame(step);
        })();
    }

    /* ── 카드 4/5: 리스트 행 등장 ── */
    function showRows(listId) {
        document.querySelectorAll(`#${listId} .rc4-row`).forEach(r => r.classList.add('show'));
    }

    /* ── 카드 6: 타일 등장 ── */
    function showTiles() {
        document.querySelectorAll('#recap-bento .rc6-tile').forEach(t => t.classList.add('show'));
    }

    /* ── 카드 진입 시 트리거 ── */
    function onEnter(idx, data) {
        if (idx === 0) setTimeout(() => animScore(data.score), 150);
        if (idx === 1) setTimeout(() => drawRadar(data.radar), 260);
        if (idx === 3) setTimeout(() => showRows('recap-housing-list'), 100);
        if (idx === 4) setTimeout(() => showRows('recap-finance-list'), 100);
        if (idx === 5) setTimeout(() => showTiles(), 100);
    }

    /* ── 카드 전환 ── */
    function move(dir, data) {
        if (busy) return;
        const next = cur + dir;

        // 마지막 카드에서 다음 → 전체 리포트
        if (next >= TOTAL) {
            const modal = document.getElementById('recap-modal');
            if (modal && !modal.classList.contains('hidden')) {
                closeRecapModal();
            } else {
                setView('result');
            }
            return;
        }
        if (next < 0) return;

        busy = true;
        const rev = dir < 0;
        const allCards = cards();

        allCards[cur].classList.remove('active');
        allCards[cur].classList.toggle('rev', rev);
        allCards[cur].classList.add('exiting');

        const nxt = allCards[next];
        nxt.classList.toggle('rev', rev);
        nxt.classList.add('entering');

        cur = next;
        syncUI();
        onEnter(cur, data);

        setTimeout(() => {
            allCards.forEach(c => {
                if (c.classList.contains('exiting')) {
                    c.classList.remove('exiting', 'rev');
                    c.style.opacity = '0';
                }
                if (c.classList.contains('entering')) {
                    c.classList.remove('entering', 'rev');
                    c.classList.add('active');
                    c.style.opacity = '';
                }
            });
            busy = false;
        }, 520);
    }

    /* ── 공개 초기화 함수 ── */
    function init(reportData) {
        cur = 0;
        busy = false;
        radarDrawn = false;

        // 리셋: 이전 show 클래스 제거 (재진단 시)
        document.querySelectorAll('.rc4-row').forEach(r => r.classList.remove('show'));
        document.querySelectorAll('.rc6-tile').forEach(t => t.classList.remove('show'));
        document.querySelectorAll('.rc2-stat-fill').forEach(b => b.style.width = '0');

        // 첫 카드 활성화
        cards().forEach((c, i) => {
            c.classList.remove('active', 'entering', 'exiting', 'rev');
            c.style.opacity = i === 0 ? '' : '0';
            if (i === 0) c.classList.add('active');
        });

        syncUI();
        onEnter(0, reportData);

        // 버튼 이벤트 (중복 등록 방지)
        const pBtn = prevBtn();
        const nBtn = nextBtn();
        const newPrev = pBtn.cloneNode(true);
        const newNext = nBtn.cloneNode(true);
        pBtn.replaceWith(newPrev);
        nBtn.replaceWith(newNext);
        newPrev.addEventListener('click', () => move(-1, reportData));
        newNext.addEventListener('click', () => move(1, reportData));
    }

    return { init };

})();


/* ==========================================================================
   renderRecap(report) — handleMatch() 에서 setView('result') 대신 호출
   report: currentReport (form.js의 기존 변수)
   ========================================================================== */

function renderRecap(report) {
    if (!report) return;

    const {
        housing = { list: [], top_1: null, reason: '' },
        finance = { list: [], top_1: null, reason: '' },
        welfare = { list: [], top_1: null, reason: '' },
        chart_data = { radar: { 주거: 80, 금융: 74, 복지: 68, 청약: 71, 대출: 79, 혜택: 65 } },
        financial_simulation = { max_limit: 0, monthly_interest: 0 }
    } = report;

    const sim = financial_simulation;
    const radar = chart_data.radar;

    /* ── 카드 3: 금융 수치 주입 ── */
    const limitEl = document.getElementById('recap-sim-limit');
    const interestEl = document.getElementById('recap-sim-interest');
    const rateEl = document.getElementById('recap-sim-rate');
    if (limitEl) limitEl.textContent = sim.max_limit.toLocaleString();
    if (interestEl) interestEl.textContent = sim.monthly_interest.toLocaleString();
    if (rateEl) rateEl.textContent = sim.base_rate ?? '1.8';

    /* ── 카드 2: 레이더 바 data-w 동적 설정 ── */
    const fills = document.querySelectorAll('.rc2-stat-fill');
    const radarValues = Object.values(radar);
    fills.forEach((el, i) => { if (radarValues[i]) el.dataset.w = radarValues[i]; });

    /* ── 카드 4: 주거 리스트 렌더 ── */
    const housingList = document.getElementById('recap-housing-list');
    if (housingList) {
        const items = [housing.top_1, ...(housing.list || [])].filter(Boolean).slice(0, 3);
        housingList.innerHTML = items.map((p, i) => recapPolicyRow(p, i + 1)).join('');
    }

    /* ── 카드 5: 금융 리스트 렌더 ── */
    const financeList = document.getElementById('recap-finance-list');
    if (financeList) {
        const items = [finance.top_1, ...(finance.list || [])].filter(Boolean).slice(0, 3);
        financeList.innerHTML = items.map((p, i) => recapFinanceRow(p, i + 1)).join('');
    }

    /* ── 카드 6: 복지 벤토 렌더 ── */
    const bento = document.getElementById('recap-bento');
    if (bento) {
        const items = [welfare.top_1, ...(welfare.list || [])].filter(Boolean).slice(0, 6);
        bento.innerHTML = items.map((p, i) => recapBentoTile(p, i + 1)).join('');
    }

    /* ── 종합 점수 계산 ── */
    const score = Math.round(Object.values(radar).reduce((a, b) => a + b, 0) / Object.values(radar).length);
    const scoreEl = document.getElementById('recap-score-num');
    if (scoreEl) scoreEl.innerHTML = '0<sub>%</sub>';

    /* ── localStorage 저장 (리캡 시작 시점에 바로 저장) ── */
    try {
        localStorage.setItem('myreport_data', JSON.stringify(report));
        localStorage.setItem('myreport_saved_at', new Date().toISOString());
    } catch(e) {}

    /* ── Recap 뷰 전환 후 초기화 ── */
    setView('recap');
    Recap.init({ score, radar });
}

function recapPolicyRow(p, rank) {
    if (!p) return '';
    const url = (p.url && p.url !== '#') ? p.url : 'https://www.youthcenter.go.kr';
    const badgeClass = rank === 1 ? 'rc-badge-1' : rank === 2 ? 'rc-badge-2' : 'rc-badge-3';
    return `
        <div class="rc4-row">
            <div class="rc-prowl">
                <div class="rc-badge ${badgeClass}">${rank}</div>
                <div style="min-width:0">
                    <div class="rc-pname">${p.title || p.name || ''}</div>
                    <div class="rc-porg">${p.org || p.bank_nm || ''}</div>
                </div>
            </div>
            <div class="rc-pright">
                <div class="rc-ppct">${p.score || 85}%</div>
                <a class="rc-clink" href="${url}" target="_blank" rel="noopener noreferrer">공고 확인 →</a>
            </div>
        </div>`;
}

function recapFinanceRow(p, rank) {
    if (!p) return '';
    const url = (p.url && p.url !== '#') ? p.url : 'https://www.youthcenter.go.kr';
    const topClass = rank === 1 ? 'top' : '';
    return `
        <div class="rc5-item">
            <div class="rc5-rank ${topClass}">${rank}</div>
            <div class="rc5-content">
                <div class="rc5-name">${p.title || p.name || ''}</div>
                <div class="rc5-org">${p.org || p.bank_nm || ''}</div>
            </div>
            <div class="rc5-meta">
                <div class="rc5-pct">${p.score || 80}%</div>
                <a class="rc-clink" href="${url}" target="_blank" rel="noopener noreferrer" style="margin-left:8px">공고 확인 →</a>
            </div>
        </div>`;
}


function recapBentoTile(p, rank) {
    if (!p) return '';
    const url = (p.url && p.url !== '#') ? p.url : 'https://www.youthcenter.go.kr';
    const hi = rank <= 2 ? 'hi' : '';
    return `
        <div class="rc6-tile ${hi}">
            <div class="rc6-tile-rank">${rank}순위</div>
            <div class="rc6-tile-name">${p.title || p.name || ''}</div>
            <div class="rc6-tile-bottom">
                <div class="rc6-tile-pct">${p.score || 80}%</div>
                <a class="rc-clink-sm" href="${url}" target="_blank" rel="noopener noreferrer">확인 →</a>
            </div>
        </div>`;
}