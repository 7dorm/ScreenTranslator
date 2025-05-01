let lastUploadedFile = null;

document.getElementById('upload').addEventListener('change', function(event) {
    const file = event.target.files[0];
    if (!file) return;

    const VIDEO_EXTENSIONS = [ 
        "avi",  "mp4",  "mov",  "mkv",  "flv", 
        "wmv",  "mpeg", "mpg",  "mpe",  "m4v",  
        "3gp",  "3g2",  "asf",  "divx", "f4v", 
        "m2ts", "m2v",  "m4p",  "mts",  "ogm", 
        "ogv",  "qt",   "rm",   "vob",  "webm",
        "xvid" 
    ];
    const IMAGE_EXTENSIONS = [
        "bmp",  "dib",  "jpeg", "jpg",  "jpe", 
        "jp2",  "png",  "pbm",  "pgm",  "ppm", 
        "sr",   "ras",  "tiff", "tif",  "webp" 
    ]
    
    const fileExtension = file.name.split('.').pop().toLowerCase();
    if (!(VIDEO_EXTENSIONS.includes(fileExtension) || IMAGE_EXTENSIONS.includes(fileExtension))) {
        alert("Неверный формат файла!");
        return;
    }
    
    lastUploadedFile = file;
    const mediaBox = document.getElementById('original-media');
    mediaBox.innerHTML = '';

    if (VIDEO_EXTENSIONS.includes(fileExtension)) {
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


async function processMedia() {
    if (!lastUploadedFile) {
        alert("Сначала загрузите файл!");
        return;
    }
    
    const formData = new FormData();
    formData.append('File', lastUploadedFile);
    
    try {
        const response = await fetch('/ScreenTranslatorAPI/fileProcess', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error("Ошибка сервера");
        }
        
        const apiResponse = await response.json();
        console.log("Ответ сервера:", apiResponse);
        const processedMedia = document.getElementById('processed-media');
        const recognizedText = document.getElementById('recognized-text');
        const translatedText = document.getElementById('translated-text');
        processedMedia.innerHTML = '';
        
        if (apiResponse['Recognized text'] && apiResponse['Recognized text'].length > 0) {
            const isVideo = lastUploadedFile.name.toLowerCase().endsWith('.mp4');
            recognizedText.value = isVideo 
                ? apiResponse['Recognized text'].join('\n') 
                : apiResponse['Recognized text'];
        }
        if (apiResponse['Translated text'] && apiResponse['Translated text'].length > 0) {
            const isVideo = lastUploadedFile.name.toLowerCase().endsWith('.mp4');
            translatedText.value = isVideo 
                ? apiResponse['Translated text'].join('\n') 
                : apiResponse['Translated text'];
        }
        
        const mediaUrl = apiResponse['Boxed url'] || apiResponse['Translated url'];
        if (mediaUrl) {
            const mediaResponse = await fetch(mediaUrl);
            if (!mediaResponse.ok) {
                throw new Error("Не удалось загрузить обработанное медиа");
            }
            
            const mediaBlob = await mediaResponse.blob();
            const mediaObjectUrl = URL.createObjectURL(mediaBlob);
            const isVideo = mediaUrl.toLowerCase().endsWith('.mp4');
            
            if (isVideo) {
                const video = document.createElement('video');
                video.src = mediaObjectUrl;
                video.controls = true;
                video.style.maxWidth = '100%';
                video.style.maxHeight = '100%';
                processedMedia.appendChild(video);
            } else {
                const img = document.createElement('img');
                img.src = mediaObjectUrl;
                img.style.maxWidth = '100%';
                img.style.maxHeight = '100%';
                processedMedia.appendChild(img);
            }
        }
    } catch (error) {
        console.error("Ошибка:", error);
        alert("Произошла ошибка при обработке файла: " + error.message);
    }
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
