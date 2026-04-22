/* ==========================================================================
   market_trends.js
   부동산 시장 동향 대시보드 전용 스크립트
   의존성: Chart.js (cdn), chartData / marketData / isMapMode (전역 변수, HTML에서 주입)
   ========================================================================== */

/**
 * 시도별 지도 마커 위치 (한국 지도 이미지 기준 %)
 * 면접 포인트: 백엔드 DB 연동 없이 CSS position absolute + %로
 * 반응형 위치를 유지하는 패턴
 */
const MARKER_POSITIONS = {
    'Seoul':    { x: 37, y: 25 }, 'Gyeonggi': { x: 44, y: 31 }, 'Incheon':  { x: 24, y: 25 },
    'Gangwon':  { x: 68, y: 22 }, 'Sejong':   { x: 44, y: 38 }, 'Daejeon':  { x: 48, y: 48 },
    'Chungnam': { x: 30, y: 42 }, 'Chungbuk': { x: 62, y: 38 }, 'Busan':    { x: 84, y: 75 },
    'Daegu':    { x: 74, y: 55 }, 'Ulsan':    { x: 88, y: 60 }, 'Gyeongbuk':{ x: 78, y: 42 },
    'Gyeongnam':{ x: 65, y: 75 }, 'Jeonbuk':  { x: 40, y: 60 }, 'Jeonnam':  { x: 28, y: 80 },
    'Gwangju':  { x: 38, y: 70 }, 'Jeju':     { x: 44, y: 92 }
};

document.addEventListener('DOMContentLoaded', () => {
    if (isMapMode) initMarkerMap();
    else initCharts();
});

/**
 * 지도 마커 렌더링
 * marketData 배열을 순회해 price-badge 엘리먼트를 동적 생성
 */
function initMarkerMap() {
    const container = document.getElementById('mapBadges');
    if (!container) return;

    marketData.forEach(item => {
        const pos = MARKER_POSITIONS[item.internal_name];
        if (!pos) return;

        const badge = document.createElement('div');
        badge.className = 'price-badge';
        badge.style.left = `${pos.x}%`;
        badge.style.top  = `${pos.y}%`;
        badge.onclick = () => { window.location.href = `?region=${item.internal_name}`; };
        badge.innerHTML = `<span>${item.region}</span>${item.avg_price.toFixed(1)}억`;
        container.appendChild(badge);
    });
}

/**
 * 지역별 차트 초기화 (라인 + 바)
 * 면접 포인트: Chart.js의 공통 옵션을 객체로 분리해 DRY하게 관리
 */
function initCharts() {
    const pEl = document.getElementById('priceChart');
    const cEl = document.getElementById('competitionChart');
    if (!pEl || !cEl) return;

    const commonOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
    };

    // 가격 추이 라인 차트
    new Chart(pEl.getContext('2d'), {
        type: 'line',
        data: {
            labels: chartData.labels,
            datasets: [{
                label: '가격(억)',
                data: chartData.prices,
                borderColor: '#6366f1',
                backgroundColor: 'rgba(99, 102, 241, 0.08)',
                fill: true,
                tension: 0.4,
                borderWidth: 3,
                pointRadius: 5,
                pointBackgroundColor: '#fff',
                pointBorderColor: '#6366f1',
                pointBorderWidth: 2,
            }]
        },
        options: {
            ...commonOptions,
            scales: {
                y: {
                    grid: { borderDash: [5, 5], color: 'rgba(99,102,241,0.08)' },
                    ticks: { font: { weight: '700' }, color: '#64748b' }
                },
                x: {
                    grid: { display: false },
                    ticks: { font: { weight: '700' }, color: '#64748b' }
                }
            }
        }
    });

    // 경쟁률 바 차트
    new Chart(cEl.getContext('2d'), {
        type: 'bar',
        data: {
            labels: chartData.labels,
            datasets: [{
                label: '경쟁률',
                data: chartData.competition,
                backgroundColor: 'rgba(99, 102, 241, 0.75)',
                borderRadius: 8,
                borderSkipped: false,
            }]
        },
        options: {
            ...commonOptions,
            scales: {
                y: { grid: { display: false }, ticks: { color: '#64748b', font: { weight: '700' } } },
                x: { grid: { display: false }, ticks: { color: '#64748b', font: { weight: '700' } } }
            }
        }
    });
}