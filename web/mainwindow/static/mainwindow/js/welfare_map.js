document.addEventListener('DOMContentLoaded', function() {
    const regionButtons = document.querySelectorAll('.region-btn');

    regionButtons.forEach(button => {
        button.addEventListener('click', function() {
            // 기존 활성화 해제
            regionButtons.forEach(btn => btn.classList.remove('active'));
            
            // 클릭한 버튼 활성화
            this.classList.add('active');

            const regionName = this.textContent.trim();
            const searchQuery = regionName + " 주거복지센터";
            
            console.log(regionName + " 지역 주거복지센터 카카오맵 검색을 실행합니다.");
            
            // 카카오맵 URL Scheme 활용 (API 키 불필요)
            // https://map.kakao.com/link/search/[검색어]
            const kakaoMapUrl = `https://map.kakao.com/link/search/${encodeURIComponent(searchQuery)}`;
            
            // 새 창에서 띄우기
            window.open(kakaoMapUrl, '_blank');
        });
    });
});