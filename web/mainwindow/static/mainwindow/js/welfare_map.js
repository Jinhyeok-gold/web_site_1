document.addEventListener('DOMContentLoaded', function() {
    const regionButtons = document.querySelectorAll('.region-btn');

    regionButtons.forEach(button => {
        button.addEventListener('click', function() {
            // 기존 활성화 해제
            regionButtons.forEach(btn => btn.classList.remove('active'));
            
            // 클릭한 버튼 활성화
            this.classList.add('active');

            const regionName = this.textContent;
            console.log(regionName + " 지역 데이터를 불러옵니다.");
            
            // 여기에 지도 이미지를 교체하거나 특정 마커를 강조하는 로직을 추가할 수 있습니다.
        });
    });
});