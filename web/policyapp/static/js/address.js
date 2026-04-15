function execDaumPostcode() {
    new daum.Postcode({
        oncomplete: function(data) {
            document.getElementById('display_address').value = data.address;
            document.getElementById('sido').value = data.sido;
            document.getElementById('sigungu').value = data.sigungu;
        }
    }).open();
}