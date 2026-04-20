/* ==========================================================================
   myreport.js — Bento v2
   ========================================================================== */

const saved   = localStorage.getItem('myreport_data');
const savedAt = localStorage.getItem('myreport_saved_at');
const DEFAULT_ORDER = ['gauge','sim-limit','sim-interest','radar','housing','finance','welfare'];

document.addEventListener('DOMContentLoaded', () => {
  // 1. 데이터 소스 결정: 서버 데이터(로그인 시) > 로컬 데이터
  let dataToRender = null;
  let dataSource = 'local';

  if (typeof serverReportData !== 'undefined' && serverReportData !== null) {
    dataToRender = serverReportData;
    dataSource = 'server';
    // 서버 데이터를 로컬에도 동기화 (오프라인/캐시 대비)
    localStorage.setItem('myreport_data', JSON.stringify(serverReportData));
    localStorage.setItem('myreport_saved_at', new Date().toISOString());
  } else if (saved) {
    dataToRender = JSON.parse(saved);
  }

  if (dataToRender) {
    document.getElementById('mr-empty').style.display = 'none';
    document.getElementById('mr-grid').classList.remove('hidden');
    
    // 저장 시점 표시
    const displayDate = dataSource === 'server' ? new Date() : (savedAt ? new Date(savedAt) : new Date());
    document.getElementById('mr-meta-date').style.display = 'flex';
    document.getElementById('mr-saved-date').textContent =
      displayDate.toLocaleDateString('ko-KR', { year:'numeric', month:'long', day:'numeric' }) + 
      (dataSource === 'server' ? ' (실시간 동기화)' : ' 저장');

    renderResultsForMyReport(dataToRender);
    restoreLayout();
  }
  initDrag();
  initResize();
});

/* ==========================================================================
   렌더링
   ========================================================================== */
function renderResultsForMyReport(report) {
  if (!report) return;
  const {
    housing = { list:[], top_1:null, reason:'' },
    finance  = { list:[], top_1:null, reason:'' },
    welfare  = { list:[], top_1:null, reason:'' },
    chart_data = { radar:{} },
    financial_simulation = { max_limit:0, monthly_interest:0 }
  } = report;

  const sim   = financial_simulation;
  const radar = chart_data?.radar || {};

  /* 종합 점수 계산 */
  const vals  = Object.values(radar);
  const score = vals.length ? Math.round(vals.reduce((a,b) => a+b, 0) / vals.length) : 0;

  /* 수치 카운트업 */
  animateBentoNum('gauge-score-val',    score);
  animateBentoNum('sim-limit-val',      sim.max_limit || 0);
  animateBentoNum('sim-interest-val',   sim.monthly_interest || 0);

  /* SVG 게이지 애니메이션 */
  animateSvgGauge(score);

  /* form.js renderVisuals → 레이더 차트 그리기 */
  renderVisuals(chart_data, sim);

  /* 레이더 컬러 오버라이드 */
  requestAnimationFrame(() => {
    if (window.activeCharts?.gauge) {
      window.activeCharts.gauge.data.datasets[0].backgroundColor[0] = '#5b5ef4';
      window.activeCharts.gauge.update('none');
    }
    if (window.activeCharts?.radar) {
      const r = window.activeCharts.radar;
      r.data.datasets[0].backgroundColor     = 'rgba(91,94,244,.15)';
      r.data.datasets[0].borderColor          = '#5b5ef4';
      r.data.datasets[0].pointBackgroundColor = '#5b5ef4';
      r.data.datasets[0].borderWidth          = 2.5;
      r.update('none');
    }
  });

  renderWidgetCards('mr-housing-container', housing, 'Housing');
  renderWidgetCards('mr-finance-container', finance,  'Finance');
  renderWidgetCards('mr-welfare-container', welfare,  'Welfare');
}

/**
 * Radar 차트를 그리는 통합 함수 (Chart.js 활용)
 */
function renderVisuals(chart_data, sim) {
  const radarData = chart_data.radar;
  const radarCtx = document.getElementById('radarChartCanvas')?.getContext('2d');
  if (!radarCtx) return;

  // 기존 차트가 있으면 파괴 (메모리 관리 및 오버랩 방지)
  if (window.activeCharts && window.activeCharts.radar) {
    window.activeCharts.radar.destroy();
  } else if (!window.activeCharts) {
    window.activeCharts = { radar: null };
  }

  window.activeCharts.radar = new Chart(radarCtx, {
    type: 'radar',
    data: {
      labels: Object.keys(radarData),
      datasets: [{
        label: '추천 적합도',
        data: Object.values(radarData),
        backgroundColor: 'rgba(91, 94, 244, 0.2)',
        borderColor: '#5b5ef4',
        pointBackgroundColor: '#5b5ef4',
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
          grid: { color: 'rgba(0,0,0,0.05)' },
          pointLabels: { font: { size: 11, weight: '600' }, color: '#6e6e8a' }
        }
      },
      plugins: { legend: { display: false } }
    }
  });
}

/* SVG 게이지 애니메이션 */
function animateSvgGauge(score) {
  const arc = document.getElementById('mr-gauge-arc');
  if (!arc) return;
  const r = 48;
  const circ = 2 * Math.PI * r;          // ≈ 301.6
  const offset = circ * 0.25;             // 시작점 조정 (12시 위치)
  const target  = circ * (score / 100);
  const gap     = circ - target;

  let start = null;
  const duration = 1400;
  function step(ts) {
    if (!start) start = ts;
    const p    = Math.min((ts - start) / duration, 1);
    const ease = 1 - Math.pow(1 - p, 3);
    const cur  = target * ease;
    arc.setAttribute('stroke-dasharray', `${cur} ${circ - cur}`);
    if (p < 1) requestAnimationFrame(step);
  }
  requestAnimationFrame(step);
}

/* 카운트업 */
function animateBentoNum(id, target) {
  const el = document.getElementById(id);
  if (!el) return;
  const duration = 1200, start = performance.now();
  function step(now) {
    const ease = 1 - Math.pow(1 - Math.min((now - start) / duration, 1), 3);
    el.textContent = Math.round(ease * target).toLocaleString();
    if (ease < 1) requestAnimationFrame(step);
  }
  requestAnimationFrame(step);
}

function renderWidgetCards(containerId, data, type) {
  const el = document.getElementById(containerId);
  if (!el) return;
  let html = '';
  if (data.reason) html += `<p class="mr-reason">${data.reason}</p>`;
  html += `<div class="result-cards-row">
    ${renderPolicyCard(data.top_1, type, true)}
    ${(data.list || []).slice(0,2).map(p => renderPolicyCard(p, type)).join('')}
  </div>`;
  el.innerHTML = html;
}

function renderPolicyCard(p, type, isTop = false) {
  if (!p) return '';
  const score = p.score || 85;
  const officialUrl = (p.url && p.url !== '#') ? p.url : 'https://www.youthcenter.go.kr';
  const topMatchClass = isTop ? 'top-match' : '';
  const badgeText = isTop ? '1순위' : '추천';
  const iconHtml = ``; // Bento uses CSS borders to differentiate

  return `
      <div class="policy-card-modern ${topMatchClass}">
          <div class="card-badge">${badgeText}</div>
          <div class="card-score">${score}% 일치</div>
          <h4>${p.title || p.name}</h4>
          <div class="org-name">${p.org || p.bank_nm || '정책 거버넌스'}</div>
          <p class="card-summary">${p.summary || p.benefit || '사용자님의 프로필에 최적화된 맞춤형 지원 정책입니다.'}</p>
          <div class="card-footer">
              <a href="${officialUrl}" target="_blank" rel="noopener noreferrer" class="card-link">
                  공고 확인하기 <i class="fas fa-external-link-alt"></i>
              </a>
          </div>
      </div>
  `;
}

/* ==========================================================================
   드래그 & 드롭
   ========================================================================== */
let editMode = false, dragSrc = null, placeholder = null, dropped = false;

function createPlaceholder(ref) {
  const ph = document.createElement('div');
  ph.className = 'mr-placeholder';
  ref.classList.forEach(c => { if (c.startsWith('mr-w-')) ph.classList.add(c); });
  if (ref.style.gridColumn) ph.style.gridColumn = ref.style.gridColumn;
  ph.style.height = ref.offsetHeight + 'px';
  return ph;
}

function toggleEditMode() {
  editMode = !editMode;
  const grid    = document.getElementById('mr-grid');
  const banner  = document.getElementById('mr-edit-banner');
  const btnEdit = document.getElementById('btn-edit-mode');
  const btnReset= document.getElementById('btn-reset-layout');
  grid.classList.toggle('mr-edit-active', editMode);
  banner.classList.toggle('hidden', !editMode);
  btnReset.style.display = editMode ? 'inline-flex' : 'none';
  btnEdit.innerHTML = editMode
    ? '<i class="fas fa-check"></i> 편집 완료'
    : '<i class="fas fa-th-large"></i> 레이아웃 편집';
  if (!editMode) { cleanupPlaceholder(); saveLayout(); }
}

function cleanupPlaceholder() {
  if (placeholder?.parentNode) placeholder.parentNode.removeChild(placeholder);
  placeholder = null;
}

function flipAnimate() {
  const widgets = [...document.querySelectorAll('.mr-widget')];
  const before  = new Map();
  widgets.forEach(w => { const r = w.getBoundingClientRect(); before.set(w, { x:r.left, y:r.top }); });
  return () => {
    widgets.forEach(w => {
      const r = w.getBoundingClientRect(), prev = before.get(w);
      if (!prev) return;
      const dx = prev.x - r.left, dy = prev.y - r.top;
      if (Math.abs(dx) < 1 && Math.abs(dy) < 1) return;
      w.style.transition = 'none';
      w.style.transform  = `translate(${dx}px,${dy}px)`;
      requestAnimationFrame(() => requestAnimationFrame(() => {
        w.style.transition = 'transform .32s cubic-bezier(.25,.46,.45,.94)';
        w.style.transform  = '';
      }));
    });
  };
}

let autoScrollRAF = null;
const SCROLL_ZONE = 100, SCROLL_SPEED = 12;
function startAutoScroll(y) {
  stopAutoScroll();
  const step = () => {
    const vh = window.innerHeight;
    if (y < SCROLL_ZONE) window.scrollBy(0, -SCROLL_SPEED * (1 - y / SCROLL_ZONE));
    else if (y > vh - SCROLL_ZONE) window.scrollBy(0, SCROLL_SPEED * (1 - (vh - y) / SCROLL_ZONE));
    autoScrollRAF = requestAnimationFrame(step);
  };
  autoScrollRAF = requestAnimationFrame(step);
}
function stopAutoScroll() { if (autoScrollRAF) { cancelAnimationFrame(autoScrollRAF); autoScrollRAF = null; } }

function attachPlaceholderEvents(ph) {
  ph.addEventListener('dragover', e => { if (!editMode || !dragSrc) return; e.preventDefault(); e.dataTransfer.dropEffect = 'move'; });
  ph.addEventListener('drop', e => {
    if (!editMode || !dragSrc) return;
    e.preventDefault(); dropped = true;
    const pf = flipAnimate();
    ph.parentNode.insertBefore(dragSrc, ph);
    cleanupPlaceholder(); pf();
  });
}

function movePlaceholder(grid, target) {
  if (!placeholder) return;
  const all = [...grid.querySelectorAll('.mr-widget:not(.mr-dragging)')];
  const ti  = all.indexOf(target);
  const si  = [...grid.querySelectorAll('.mr-widget')].indexOf(dragSrc);
  grid.insertBefore(placeholder, si < ti ? target.nextSibling : target);
}

function initDrag() {
  const grid = document.getElementById('mr-grid');
  document.querySelectorAll('.mr-widget').forEach(w => {
    w.addEventListener('mouseenter', () => { if (editMode) w.setAttribute('draggable','true'); });
    w.addEventListener('mouseleave', () => { if (!dragSrc) w.setAttribute('draggable','false'); });
    w.addEventListener('dragstart', e => {
      if (!editMode) { e.preventDefault(); return; }
      dragSrc = w; dropped = false;
      e.dataTransfer.effectAllowed = 'move'; e.dataTransfer.setData('text/plain','');
      placeholder = createPlaceholder(w); attachPlaceholderEvents(placeholder);
      setTimeout(() => { w.classList.add('mr-dragging'); w.parentNode.insertBefore(placeholder, w.nextSibling); }, 0);
    });
    w.addEventListener('dragend', () => {
      w.setAttribute('draggable','false'); w.classList.remove('mr-dragging');
      if (!dropped) cleanupPlaceholder();
      stopAutoScroll(); dragSrc = null; dropped = false;
      document.querySelectorAll('.mr-widget').forEach(x => x.classList.remove('mr-drag-over'));
    });
    w.addEventListener('dragover', e => {
      if (!editMode || !dragSrc || dragSrc === w) return;
      e.preventDefault(); e.dataTransfer.dropEffect = 'move';
      startAutoScroll(e.clientY);
      document.querySelectorAll('.mr-widget').forEach(x => x.classList.remove('mr-drag-over'));
      w.classList.add('mr-drag-over'); movePlaceholder(grid, w);
    });
    w.addEventListener('drop', e => {
      if (!editMode || !dragSrc || dragSrc === w) return;
      e.preventDefault(); e.stopPropagation();
      w.classList.remove('mr-drag-over'); stopAutoScroll(); dropped = true;
      const all = [...grid.querySelectorAll('.mr-widget')];
      const si  = all.indexOf(dragSrc), ti = all.indexOf(w);
      const pf  = flipAnimate(); cleanupPlaceholder();
      grid.insertBefore(dragSrc, si < ti ? w.nextSibling : w); pf();
    });
  });
  grid.addEventListener('dragover', e => { if (!editMode) return; e.preventDefault(); startAutoScroll(e.clientY); });
  grid.addEventListener('dragleave', () => stopAutoScroll());
}

/* ==========================================================================
   리사이즈
   ========================================================================== */
const SPAN_STEPS = [
  { span:12, cards:3, cls:'mr-cards-3' },
  { span:8,  cards:2, cls:'mr-cards-2' },
  { span:4,  cards:1, cls:'mr-cards-1' },
];
function getSpanFromDelta(start, dx, gw) {
  const n = Math.max(4, Math.min(12, start - Math.round(dx / (gw/12))));
  return SPAN_STEPS.map(s=>s.span).reduce((a,b) => Math.abs(b-n)<Math.abs(a-n)?b:a);
}
function applySpan(w, span) {
  SPAN_STEPS.forEach(s => w.classList.remove(s.cls));
  w.dataset.span = span; w.style.gridColumn = `span ${span}`;
  w.classList.add(SPAN_STEPS.find(s=>s.span===span)?.cls || 'mr-cards-3');
}
function initResize() {
  document.querySelectorAll('.mr-resizable').forEach(w => {
    const h = w.querySelector('.mr-resize-handle');
    if (!h) return;
    let sx, ss;
    h.addEventListener('mousedown', e => {
      if (!editMode) return;
      e.preventDefault(); e.stopPropagation();
      sx = e.clientX; ss = parseInt(w.dataset.span || '12');
      document.body.style.cursor = 'ew-resize'; document.body.style.userSelect = 'none';
      w.classList.add('mr-resizing');
      const pv = document.createElement('div'); pv.className = 'mr-resize-preview'; w.appendChild(pv);
      const om = e => { const ns = getSpanFromDelta(ss, -(e.clientX-sx), document.getElementById('mr-grid').offsetWidth); applySpan(w, ns); pv.textContent = `카드 ${SPAN_STEPS.find(s=>s.span===ns).cards}개`; };
      const ou = () => { document.body.style.cursor=''; document.body.style.userSelect=''; w.classList.remove('mr-resizing'); pv.remove(); document.removeEventListener('mousemove',om); document.removeEventListener('mouseup',ou); saveLayout(); };
      document.addEventListener('mousemove', om); document.addEventListener('mouseup', ou);
    });
  });
}

/* ==========================================================================
   저장/복원/초기화
   ========================================================================== */
function saveLayout() {
  const order = [...document.querySelectorAll('.mr-widget')].map(w => w.dataset.widgetId);
  const spans = {};
  document.querySelectorAll('.mr-resizable').forEach(w => { if (w.dataset.span) spans[w.dataset.widgetId] = parseInt(w.dataset.span); });
  try { localStorage.setItem('myreport_layout', JSON.stringify(order)); localStorage.setItem('myreport_spans', JSON.stringify(spans)); } catch(e) {}
}
function restoreLayout() {
  try {
    const raw = localStorage.getItem('myreport_layout');
    if (raw) { const order = JSON.parse(raw); const grid = document.getElementById('mr-grid'); order.forEach(id => { const w = grid.querySelector(`[data-widget-id="${id}"]`); if (w) grid.appendChild(w); }); }
    const rawS = localStorage.getItem('myreport_spans');
    if (rawS) Object.entries(JSON.parse(rawS)).forEach(([id, span]) => { const w = document.querySelector(`[data-widget-id="${id}"]`); if (w) applySpan(w, span); });
  } catch(e) {}
}
function resetLayout() {
  try { localStorage.removeItem('myreport_layout'); localStorage.removeItem('myreport_spans'); } catch(e) {}
  const grid = document.getElementById('mr-grid'), pf = flipAnimate();
  DEFAULT_ORDER.forEach(id => {
    const w = grid.querySelector(`[data-widget-id="${id}"]`);
    if (w) { w.style.gridColumn=''; w.dataset.span=''; SPAN_STEPS.forEach(s=>w.classList.remove(s.cls)); grid.appendChild(w); }
  }); pf();
}

/* ==========================================================================
   리캡 모달
   ========================================================================== */
function openRecapModal() {
  if (!saved) return alert('저장된 리포트가 없어요.');
  document.getElementById('recap-modal').classList.remove('hidden');
  renderRecap(JSON.parse(saved)); Recap.init(JSON.parse(saved));
}
function closeRecapModal() { document.getElementById('recap-modal').classList.add('hidden'); }