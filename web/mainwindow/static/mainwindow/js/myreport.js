/* ==========================================================================
   myreport.js — 마이리포트 위젯 드래그 & 레이아웃 관리
   의존성: form.js, recap.js (먼저 로드)
   ========================================================================== */

/* ── 초기화 ── */
const saved   = localStorage.getItem('myreport_data');
const savedAt = localStorage.getItem('myreport_saved_at');

document.addEventListener('DOMContentLoaded', () => {
  if (saved) {
    document.getElementById('mr-empty').style.display = 'none';
    document.getElementById('mr-grid').classList.remove('hidden');

    if (savedAt) {
      const d = new Date(savedAt);
      document.getElementById('mr-meta-date').style.display = 'flex';
      document.getElementById('mr-saved-date').textContent =
        d.toLocaleDateString('ko-KR', { year:'numeric', month:'long', day:'numeric' }) + ' 저장';
    }

    currentReport = JSON.parse(saved);
    renderResultsForMyReport(currentReport);
    restoreLayout();
  }

  initDrag();
  initResize();
});

/* ── 위젯별 렌더링 ── */
function renderResultsForMyReport(report) {
  if (!report) return;
  const {
    housing = { list:[], top_1:null, reason:'' },
    finance  = { list:[], top_1:null, reason:'' },
    welfare  = { list:[], top_1:null, reason:'' },
    chart_data = { radar:{} },
    financial_simulation = { max_limit:0, monthly_interest:0 }
  } = report;

  renderVisuals(chart_data, financial_simulation);

  // 마이리포트 전용 — 게이지/레이더 컬러를 틸로 오버라이드
  requestAnimationFrame(() => {
    // 게이지 색상 교체
    if (window.activeCharts?.gauge) {
      const gauge = window.activeCharts.gauge;
      gauge.data.datasets[0].backgroundColor[0] = '#00c2a8';
      gauge.update('none');
    }
    // 레이더 색상 교체
    if (window.activeCharts?.radar) {
      const radar = window.activeCharts.radar;
      radar.data.datasets[0].backgroundColor = 'rgba(0,194,168,.15)';
      radar.data.datasets[0].borderColor      = '#00c2a8';
      radar.data.datasets[0].pointBackgroundColor = '#00c2a8';
      radar.update('none');
    }
  });
  renderWidgetCards('mr-housing-container', housing, 'Housing');
  renderWidgetCards('mr-finance-container', finance,  'Finance');
  renderWidgetCards('mr-welfare-container', welfare,  'Welfare');
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

/* ==========================================================================
   드래그 & 드롭 — FLIP 애니메이션 + Placeholder 미리보기
   ========================================================================== */
let editMode  = false;
let dragSrc   = null;
let placeholder = null;
let dropped   = false;

/* placeholder 생성 */
function createPlaceholder(ref) {
  const ph = document.createElement('div');
  ph.className = 'mr-placeholder';
  // grid 사이즈 클래스 복사
  ref.classList.forEach(c => { if (c.startsWith('mr-w-')) ph.classList.add(c); });
  // span이 직접 설정된 경우(리사이즈된 카드 위젯) gridColumn도 복사
  if (ref.style.gridColumn) ph.style.gridColumn = ref.style.gridColumn;
  ph.style.height = ref.offsetHeight + 'px';
  return ph;
}

/* 편집 모드 토글 */
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

  if (!editMode) {
    cleanupPlaceholder();
    saveLayout();
  }
}

function cleanupPlaceholder() {
  if (placeholder && placeholder.parentNode) {
    placeholder.parentNode.removeChild(placeholder);
  }
  placeholder = null;
}

/* FLIP 애니메이션: before 위치 기록 → DOM 변경 → after 위치로 역방향 이동 후 0으로 */
function flipAnimate() {
  const widgets = [...document.querySelectorAll('.mr-widget')];

  // FIRST: 현재 위치 기록 (변경 전)
  const before = new Map();
  widgets.forEach(w => {
    const r = w.getBoundingClientRect();
    before.set(w, { x: r.left, y: r.top });
  });

  return () => {
    // LAST: 변경 후 위치 기록
    widgets.forEach(w => {
      const r    = w.getBoundingClientRect();
      const prev = before.get(w);
      if (!prev) return;

      const dx = prev.x - r.left;
      const dy = prev.y - r.top;

      if (Math.abs(dx) < 1 && Math.abs(dy) < 1) return;

      // INVERT: 이전 위치처럼 보이도록 역방향 transform
      w.style.transition = 'none';
      w.style.transform  = `translate(${dx}px, ${dy}px)`;

      // PLAY: 다음 프레임에서 0으로 복귀 (부드러운 애니메이션)
      requestAnimationFrame(() => {
        requestAnimationFrame(() => {
          w.style.transition = 'transform 0.32s cubic-bezier(0.25, 0.46, 0.45, 0.94)';
          w.style.transform  = '';
        });
      });
    });
  };
}

/* ── 드래그 중 자동 스크롤 ── */
let autoScrollRAF = null;
const SCROLL_ZONE = 100;  // 화면 상하단 100px 이내에서 스크롤
const SCROLL_SPEED = 12;

function startAutoScroll(clientY) {
  stopAutoScroll();
  function step() {
    const vh = window.innerHeight;
    if (clientY < SCROLL_ZONE) {
      window.scrollBy(0, -SCROLL_SPEED * (1 - clientY / SCROLL_ZONE));
    } else if (clientY > vh - SCROLL_ZONE) {
      window.scrollBy(0, SCROLL_SPEED * (1 - (vh - clientY) / SCROLL_ZONE));
    }
    autoScrollRAF = requestAnimationFrame(step);
  }
  autoScrollRAF = requestAnimationFrame(step);
}

function stopAutoScroll() {
  if (autoScrollRAF) { cancelAnimationFrame(autoScrollRAF); autoScrollRAF = null; }
}

/* ── placeholder에 drop 연결 헬퍼 ── */
function attachPlaceholderEvents(ph) {
  ph.addEventListener('dragover', e => {
    if (!editMode || !dragSrc) return;
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
  });

  ph.addEventListener('drop', e => {
    if (!editMode || !dragSrc) return;
    e.preventDefault();
    dropped = true;
    const playFlip = flipAnimate();
    const parent = ph.parentNode;
    parent.insertBefore(dragSrc, ph);
    cleanupPlaceholder();
    playFlip();
  });
}

/* ── placeholder 위치 업데이트 헬퍼 ── */
function movePlaceholder(grid, targetWidget) {
  if (!placeholder) return;
  const allWidgets = [...grid.querySelectorAll('.mr-widget:not(.mr-dragging)')];
  const tgtIdx = allWidgets.indexOf(targetWidget);
  const srcIdx = [...grid.querySelectorAll('.mr-widget')].indexOf(dragSrc);
  if (srcIdx < tgtIdx) {
    grid.insertBefore(placeholder, targetWidget.nextSibling);
  } else {
    grid.insertBefore(placeholder, targetWidget);
  }
}

/* 드래그 초기화 */
function initDrag() {
  const grid = document.getElementById('mr-grid');

  document.querySelectorAll('.mr-widget').forEach(widget => {

    /* 편집 모드일 때 위젯 전체 드래그 가능 */
    widget.addEventListener('mouseenter', () => {
      if (editMode) widget.setAttribute('draggable', 'true');
    });
    widget.addEventListener('mouseleave', () => {
      if (!dragSrc) widget.setAttribute('draggable', 'false');
    });

    widget.addEventListener('dragstart', e => {
      if (!editMode) { e.preventDefault(); return; }
      dragSrc = widget;
      dropped = false;
      e.dataTransfer.effectAllowed = 'move';
      e.dataTransfer.setData('text/plain', '');

      placeholder = createPlaceholder(widget);
      attachPlaceholderEvents(placeholder);

      setTimeout(() => {
        widget.classList.add('mr-dragging');
        widget.parentNode.insertBefore(placeholder, widget.nextSibling);
      }, 0);
    });

    widget.addEventListener('dragend', () => {
      widget.setAttribute('draggable', 'false');
      widget.classList.remove('mr-dragging');
      // drop이 성공적으로 일어났으면 cleanup은 drop에서 이미 처리됨
      if (!dropped) cleanupPlaceholder();
      stopAutoScroll();
      dragSrc = null;
      dropped = false;
      document.querySelectorAll('.mr-widget').forEach(w => w.classList.remove('mr-drag-over'));
    });

    widget.addEventListener('dragover', e => {
      if (!editMode || !dragSrc || dragSrc === widget) return;
      e.preventDefault();
      e.dataTransfer.dropEffect = 'move';

      startAutoScroll(e.clientY);

      document.querySelectorAll('.mr-widget').forEach(w => w.classList.remove('mr-drag-over'));
      widget.classList.add('mr-drag-over');
      movePlaceholder(grid, widget);
    });

    widget.addEventListener('drop', e => {
      if (!editMode || !dragSrc || dragSrc === widget) return;
      e.preventDefault();
      e.stopPropagation();
      widget.classList.remove('mr-drag-over');
      stopAutoScroll();
      dropped = true;

      const all    = [...grid.querySelectorAll('.mr-widget')];
      const srcIdx = all.indexOf(dragSrc);
      const tgtIdx = all.indexOf(widget);

      const playFlip = flipAnimate();
      cleanupPlaceholder();
      if (srcIdx < tgtIdx) {
        grid.insertBefore(dragSrc, widget.nextSibling);
      } else {
        grid.insertBefore(dragSrc, widget);
      }
      playFlip();
    });
  });

  /* 그리드 빈 공간 dragover 허용 + 자동 스크롤 */
  grid.addEventListener('dragover', e => {
    if (!editMode) return;
    e.preventDefault();
    startAutoScroll(e.clientY);
  });

  grid.addEventListener('dragleave', () => stopAutoScroll());
}

/* ==========================================================================
   카드 위젯 리사이즈 — span 단계로 조절 (12 → 8 → 4)
   span 12 = 카드 3개 / span 8 = 카드 2개 / span 4 = 카드 1개
   ========================================================================== */
const SPAN_STEPS = [
  { span: 12, cards: 3, cls: 'mr-cards-3' },
  { span: 8,  cards: 2, cls: 'mr-cards-2' },
  { span: 4,  cards: 1, cls: 'mr-cards-1' },
];

// 드래그 델타 → 어느 span 단계인지 결정
// 그리드 1칸 너비를 기준으로 4칸 이상 줄이면 한 단계 내려감
function getSpanFromDelta(startSpan, deltaX, gridWidth) {
  const colW = gridWidth / 12;
  const colDelta = Math.round(deltaX / colW);
  const newSpan = Math.max(4, Math.min(12, startSpan - colDelta));
  // 4, 8, 12 중 가장 가까운 값으로 스냅
  const snapped = SPAN_STEPS.map(s => s.span).reduce((a, b) =>
    Math.abs(b - newSpan) < Math.abs(a - newSpan) ? b : a
  );
  return snapped;
}

function applySpan(widget, span) {
  SPAN_STEPS.forEach(s => widget.classList.remove(s.cls));
  const step = SPAN_STEPS.find(s => s.span === span) || SPAN_STEPS[0];
  widget.dataset.span = span;
  widget.classList.add(step.cls);
  // mr-w-full 클래스 대신 data-span CSS가 적용되도록
  widget.style.gridColumn = `span ${span}`;
}

function initResize() {
  document.querySelectorAll('.mr-resizable').forEach(widget => {
    const handle = widget.querySelector('.mr-resize-handle');
    if (!handle) return;

    let startX, startSpan;

    handle.addEventListener('mousedown', e => {
      if (!editMode) return;
      e.preventDefault();
      e.stopPropagation();

      startX    = e.clientX;
      startSpan = parseInt(widget.dataset.span || '12');

      document.body.style.cursor    = 'ew-resize';
      document.body.style.userSelect = 'none';
      widget.classList.add('mr-resizing');

      // 실시간 미리보기 span 표시
      const preview = document.createElement('div');
      preview.className = 'mr-resize-preview';
      widget.appendChild(preview);

      function onMove(e) {
        const grid    = document.getElementById('mr-grid');
        const gridW   = grid.offsetWidth;
        const dx      = e.clientX - startX;
        const newSpan = getSpanFromDelta(startSpan, -dx, gridW);
        applySpan(widget, newSpan);

        const step = SPAN_STEPS.find(s => s.span === newSpan);
        preview.textContent = `카드 ${step.cards}개`;
      }

      function onUp() {
        document.body.style.cursor    = '';
        document.body.style.userSelect = '';
        widget.classList.remove('mr-resizing');
        preview.remove();
        document.removeEventListener('mousemove', onMove);
        document.removeEventListener('mouseup', onUp);
        saveLayout();
      }

      document.addEventListener('mousemove', onMove);
      document.addEventListener('mouseup', onUp);
    });
  });
}

function restoreWidgetSpans(spans) {
  if (!spans) return;
  Object.entries(spans).forEach(([id, span]) => {
    const widget = document.querySelector(`[data-widget-id="${id}"]`);
    if (widget) applySpan(widget, span);
  });
}

/* ── 레이아웃 저장/복원/초기화 ── */
function saveLayout() {
  const order = [...document.querySelectorAll('.mr-widget')].map(w => w.dataset.widgetId);
  const spans = {};
  document.querySelectorAll('.mr-resizable').forEach(w => {
    if (w.dataset.span) spans[w.dataset.widgetId] = parseInt(w.dataset.span);
  });
  try {
    localStorage.setItem('myreport_layout', JSON.stringify(order));
    localStorage.setItem('myreport_spans',  JSON.stringify(spans));
  } catch(e) {}
}

function restoreLayout() {
  try {
    const raw = localStorage.getItem('myreport_layout');
    if (raw) {
      const order = JSON.parse(raw);
      const grid  = document.getElementById('mr-grid');
      order.forEach(id => {
        const w = grid.querySelector(`[data-widget-id="${id}"]`);
        if (w) grid.appendChild(w);
      });
    }
    const rawS = localStorage.getItem('myreport_spans');
    if (rawS) restoreWidgetSpans(JSON.parse(rawS));
  } catch(e) {}
}

function resetLayout() {
  try {
    localStorage.removeItem('myreport_layout');
    localStorage.removeItem('myreport_spans');
  } catch(e) {}

  const grid = document.getElementById('mr-grid');
  const playFlip = flipAnimate();
  ['gauge','radar','simulation','housing','finance','welfare'].forEach(id => {
    const w = grid.querySelector(`[data-widget-id="${id}"]`);
    if (w) {
      w.style.gridColumn = '';
      w.dataset.span     = '';
      SPAN_STEPS.forEach(s => w.classList.remove(s.cls));
      grid.appendChild(w);
    }
  });
  playFlip();
}

/* ── 리캡 모달 ── */
function openRecapModal() {
  if (!saved) return alert('저장된 리포트가 없어요.');
  document.getElementById('recap-modal').classList.remove('hidden');
  renderRecap(JSON.parse(saved));
  Recap.init(JSON.parse(saved));
}

function closeRecapModal() {
  document.getElementById('recap-modal').classList.add('hidden');
}