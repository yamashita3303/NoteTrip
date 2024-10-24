// 今日の日付を設定
document.addEventListener('DOMContentLoaded', function () {
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('departure-date').value = today;  // 出発日
    document.getElementById('return-date').value = today;     // 帰宅日
});

// 画像のプレビューを表示
function previewImage(event) {
    const imagePreview = document.getElementById('image-preview');
    const file = event.target.files[0];
    const reader = new FileReader();

    reader.onload = function(e) {
        imagePreview.src = e.target.result;
        imagePreview.style.display = 'block'; // 画像を表示
    }

    if (file) {
        reader.readAsDataURL(file); // 画像ファイルを読み込む
    }
}
