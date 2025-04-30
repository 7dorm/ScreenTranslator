let lastUploadedFile = null;

document.getElementById('upload').addEventListener('change', function(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    const allowedExtensions = ['bmp', 'jpeg', 'jpg', 'png', 'mp4'];
    const fileExtension = file.name.split('.').pop().toLowerCase();
    if (!allowedExtensions.includes(fileExtension)) {
        alert("Неверный формат файла! Поддерживаются: .bmp, .jpeg, .jpg, .png, .mp4");
        return;
    }
    
    lastUploadedFile = file;
    const mediaBox = document.getElementById('original-media');
    mediaBox.innerHTML = '';

    if (fileExtension === 'mp4') {
        const video = document.createElement('video');
        video.src = URL.createObjectURL(file);
        video.controls = true;
        video.style.maxWidth = '100%';
        video.style.maxHeight = '100%';
        mediaBox.appendChild(video);
    } else {
        const reader = new FileReader();
        reader.onload = function(e) {
            mediaBox.innerHTML = `<img src="${e.target.result}" style="max-width:100%; max-height:100%;">`;
        };
        reader.readAsDataURL(file);
    }
});

function processMedia() {
    if (!lastUploadedFile) {
        alert("Сначала загрузите файл!");
        return;
    }
    
    const formData = new FormData();
    formData.append('file', lastUploadedFile);
    
    fetch('/ScreenTranslatorAPI/translate', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) throw new Error("Ошибка сервера");
            return response.blob(); // Получаем zip как blob
    })
    .then(JSZip.loadAsync) // Распаковываем zip
    .then(zip => {
        const processedMedia = document.getElementById('processed-media');
        const recognizedText = document.getElementById('recognized-text');
        const translatedText = document.getElementById('translated-text');
        processedMedia.innerHTML = '';

        // 1. Обработка распознанного текста
        zip.file("recognized_text.txt")?.async("string").then(text => {
            recognizedText.value = text;
        });

        // 2. Обработка переведённого текста
        zip.file("translated_text.txt")?.async("string").then(text => {
            translatedText.value = text;
        });

        // 3. Отображение изображения/видео с переводом
        const tryDisplayFile = async (filename, isVideo = false) => {
            const file = zip.file(filename);
            if (file) {
                const blob = await file.async("blob");
                const url = URL.createObjectURL(blob);

                if (isVideo || filename.endsWith(".mp4")) {
                    const video = document.createElement('video');
                    video.src = url;
                    video.controls = true;
                    video.style.maxWidth = '100%';
                    video.style.maxHeight = '100%';
                    processedMedia.appendChild(video);
                } else {
                    const img = document.createElement('img');
                    img.src = url;
                    img.style.maxWidth = '100%';
                    img.style.maxHeight = '100%';
                    processedMedia.appendChild(img);
                }
            }
        };

        // 4. Находим файл, начинающийся с "translated_output" и определяем его тип по расширению
        (async () => {
            for (const [filename, zipEntry] of Object.entries(zip.files)) {
                if (filename.startsWith("translated_output")) {
                    const lower = filename.toLowerCase();
                    const isVideo = lower.endsWith(".mp4");
                    await tryDisplayFile(filename, isVideo);
                    break; // Показываем только первый найденный подходящий файл
                }
            }
        })();
    })
    .catch(error => console.error("Ошибка:", error));
}

function saveMedia() {
    const processedMedia = document.querySelector("#processed-media img, #processed-media video");
    if (!processedMedia) {
        alert("Нет обработанного файла для сохранения!");
        return;
    }
    
    const link = document.createElement("a");
    link.href = processedMedia.src;
    link.download = processedMedia.tagName === 'VIDEO' ? "processed_video.mp4" : "processed_image.png";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}
