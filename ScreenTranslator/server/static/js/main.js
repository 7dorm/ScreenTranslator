document.addEventListener('DOMContentLoaded', () => {
    const apidocsBtn = document.getElementById('apidocs-btn');
    const uploadInput = document.getElementById('upload');
    const uploadBtn = document.getElementById('upload-btn');
    const processBtn = document.getElementById('process-btn');
    const saveBtn = document.getElementById('save-btn');
    const originalImage = document.getElementById('original-image');
    const originalVideo = document.getElementById('original-video');
    const processedImage = document.getElementById('processed-image');
    const processedVideo = document.getElementById('processed-video');
    const text1 = document.getElementById('text1');
    const text2 = document.getElementById('text2');
    const status = document.getElementById('status');
    const paramsForm = document.getElementById('params-form');
    const displayRadios = document.getElementsByName('processed-file');
    const textRadios = document.getElementsByName('text-display');
    const VIDEO_EXTENSIONS = [
        "avi", "mp4", "mov", "mkv", "flv",
        "wmv", "mpeg", "mpg", "mpe", "m4v",
        "3gp", "3g2", "asf", "divx", "f4v",
        "m2ts", "m2v", "m4p", "mts", "ogm",
        "ogv", "qt", "rm", "vob", "webm",
        "xvid"
    ];
    const IMAGE_EXTENSIONS = [
        "bmp", "dib", "jpeg", "jpg", "jpe",
        "jp2", "png", "pbm", "pgm", "ppm",
        "sr", "ras", "tiff", "tif", "webp"
    ];
    const ALLOWED_EXTENSIONS = VIDEO_EXTENSIONS.concat(IMAGE_EXTENSIONS);
    const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB
    let currentFile = null;
    let processedData = null;

    function updateHints() {
        const textDisplayValue = document.querySelector('input[name="text-display"]:checked').value;
        let text1Hint, text2Hint;
        
        switch(textDisplayValue) {
            case 'text-corrected':
                text1Hint = 'Corrected recognized text will appear here';
                text2Hint = 'Corrected translated text will appear here';
                break;
            case 'text-rough':
                text1Hint = 'Rough recognized text will appear here';
                text2Hint = 'Rough translated text will appear here';
                break;
            case 'text-bboxes':
                text1Hint = 'Character bounding boxes data will appear here';
                text2Hint = 'Word bounding boxes data will appear here';
                break;
        }
        
        document.getElementById('text1-hint').textContent = text1Hint;
        document.getElementById('text2-hint').textContent = text2Hint;
        const processedFileValue = document.querySelector('input[name="processed-file"]:checked').value;
        let processedHint;
        
        switch(processedFileValue) {
            case 'corrected':
                processedHint = 'Corrected text with translation overlay will appear here';
                break;
            case 'rough':
                processedHint = 'Rough text with translation overlay will appear here';
                break;
            case 'char-bb':
                processedHint = 'Character bounding boxes will appear here';
                break;
            case 'word-bb':
                processedHint = 'Word bounding boxes will appear here';
                break;
        }
        
        document.getElementById('processed-hint').textContent = processedHint;
        const hint1 = text1.previousElementSibling;
        hint1.style.display = text1.value ? 'none' : 'block';
        const hint2 = text2.previousElementSibling;
        hint2.style.display = text2.value ? 'none' : 'block';
    }
    
    // Для медиа-элементов
    const mediaBoxes = document.querySelectorAll('.media-box');
    mediaBoxes.forEach(box => {
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.attributeName === 'style') {
                    const img = box.querySelector('img');
                    const video = box.querySelector('video');
                    const hint = box.querySelector('.hint');
                    
                    if ((img && !img.style.display.includes('none')) || 
                        (video && !video.style.display.includes('none'))) {
                        hint.style.display = 'none';
                    } else {
                        hint.style.display = 'block';
                    }
                }
            });
        });
        
        observer.observe(box, { attributes: true, subtree: true });
    });

    apidocsBtn.addEventListener('click', () => window.open('/apidocs', '_blank'));

    uploadBtn.addEventListener('click', () => uploadInput.click());

    uploadInput.addEventListener('change', async (e) => {
        const file = e.target.files[0];
        if (!file) {
            status.textContent = 'Error: No file selected.';
            return;
        }
        const ext = file.name.split('.').pop().toLowerCase();
        if (!ALLOWED_EXTENSIONS.includes(ext)) {
            status.textContent = `Error: Unsupported file type. Use ${IMAGE_EXTENSIONS.join(', ')} for images or ${VIDEO_EXTENSIONS.join(', ')} for videos.`;
            uploadInput.value = '';
            return;
        }
        // Compress image
        if (IMAGE_EXTENSIONS.includes(ext)) {
            const img = new Image();
            const url = URL.createObjectURL(file);
            img.src = url;
            await new Promise((resolve) => (img.onload = resolve));
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            const maxSize = 1920;
            let width = img.width;
            let height = img.height;
            if (width > height && width > maxSize) {
                height *= maxSize / width;
                width = maxSize;
            } else if (height > maxSize) {
                width *= maxSize / height;
                height = maxSize;
            }
            canvas.width = width;
            canvas.height = height;
            ctx.drawImage(img, 0, 0, width, height);
            const compressedFile = await new Promise((resolve) =>
                canvas.toBlob((blob) => resolve(new File([blob], file.name, { type: 'image/jpeg' })), 'image/jpeg', 0.85)
            );
            URL.revokeObjectURL(url);
            if (compressedFile.size > MAX_FILE_SIZE) {
                status.textContent = 'Error: Compressed file still exceeds 10MB.';
                uploadInput.value = '';
                return;
            }
            currentFile = compressedFile;
        } else {
            currentFile = file;
        }
        processBtn.disabled = false;
        saveBtn.disabled = true;
        status.textContent = 'File selected. Click "Process" to start.';
        const url = URL.createObjectURL(currentFile);
        if (IMAGE_EXTENSIONS.includes(ext)) {
            originalImage.src = url;
            originalImage.style.display = 'block';
            originalVideo.style.display = 'none';
        } else if (VIDEO_EXTENSIONS.includes(ext)) {
            originalVideo.src = url;
            originalVideo.style.display = 'block';
            originalImage.style.display = 'none';
        }
    });

    // Update displayed image based on radiobutton selection
    const updateDisplayedImage = () => {
        if (!processedData) return;
        const selectedDisplay = Array.from(displayRadios).find(radio => radio.checked)?.value;
        processedImage.style.display = 'block';
        processedVideo.style.display = 'none';
        switch (selectedDisplay) {
            case 'corrected':
                processedImage.src = processedData['Image translated corrected url'];
                break;
            case 'rough':
                processedImage.src = processedData['Image translated rough url'];
                break;
            case 'char-bb':
                processedImage.src = processedData['Image boxed symbols url'];
                break;
            case 'word-bb':
                processedImage.src = processedData['Image boxed words url'];
                break;
            default:
                processedImage.src = '';
                processedImage.style.display = 'none';
        }
    };

    // Update displayed text based on radiobutton selection
    const updateDisplayedText = () => {
        if (!processedData) return;
        const selectedText = Array.from(textRadios).find(radio => radio.checked)?.value;
        switch (selectedText) {
            case 'text-corrected':
                text1.value = processedData['Text corrected recognized'] || '';
                text2.value = processedData['Text corrected translated'] || '';
                break;
            case 'text-rough':
                text1.value = processedData['Text rough recognized'] || '';
                text2.value = processedData['Text rough translated'] || '';
                break;
            case 'text-bboxes':
                text1.value = processedData['Bounding boxes symbols'] || '';
                text2.value = processedData['Bounding boxes words'] || '';
                break;
            default:
                text1.value = '';
                text2.value = '';
        }
    };

    // Add event listeners to radiobuttons
    displayRadios.forEach(radio => {
        radio.addEventListener('change', updateDisplayedImage)
        radio.addEventListener('change', updateHints)
    });
    textRadios.forEach(radio => {
        radio.addEventListener('change', updateDisplayedText)
        radio.addEventListener('change', updateHints)
    });

    // Process Button: Send file and parameters to backend
    processBtn.addEventListener('click', async () => {
        if (!currentFile) {
            status.textContent = 'Error: No file selected.';
            return;
        }
        status.textContent = 'Processing...';
        processBtn.disabled = true;
        processedImage.style.display = 'none';
        processedVideo.style.display = 'none';
        text1.value = '';
        text2.value = '';
        updateHints();
        // Collect and validate parameters
        const formData = new FormData(paramsForm);
        const params = {
            size: parseInt(formData.get('size')),
            conf: parseFloat(formData.get('conf')),
            iou: parseFloat(formData.get('iou')),
            max_det: parseInt(formData.get('max_det')),
            agnostic: formData.get('agnostic') === 'on',
            multi_label: formData.get('multi_label') === 'on',
            amp: formData.get('amp') === 'on',
            half_precision: formData.get('half_precision') === 'on',
        };
        // Client-side validation
        if (params.size < 320 || params.size > 3840) {
            status.textContent = 'Error: Image size must be between 320 and 3840.';
            processBtn.disabled = false;
            return;
        }
        if (params.conf < 0 || params.conf > 1) {
            status.textContent = 'Error: Confidence threshold must be between 0 and 1.';
            processBtn.disabled = false;
            return;
        }
        if (params.iou < 0 || params.iou > 1) {
            status.textContent = 'Error: IoU threshold must be between 0 and 1.';
            processBtn.disabled = false;
            return;
        }
        if (params.max_det < 1 || params.max_det > 10000) {
            status.textContent = 'Error: Maximum detections must be between 1 and 10000.';
            processBtn.disabled = false;
            return;
        }
        const uploadFormData = new FormData();
        uploadFormData.append('File', currentFile);
        uploadFormData.append('Params', JSON.stringify(params));
        try {
            // Debug FormData content
            let formDataContent = '';
            for (const [key, value] of uploadFormData.entries()) {
                formDataContent += `${key}: ${value instanceof File ? value.name : value}\n`;
            }
            console.log('FormData:', formDataContent);
            const response = await fetch('/ScreenTranslatorAPI/process', {
                method: 'POST',
                body: uploadFormData,
            });
            const result = await response.json();
            console.log('Process response:', result);
            if (response.ok) {
                status.textContent = 'Processing complete.';
                processedData = {
                    'Image boxed symbols url': result['Image boxed symbols url'],
                    'Image boxed words url': result['Image boxed words url'],
                    'Image translated rough url': result['Image translated rough url'],
                    'Image translated corrected url': result['Image translated corrected url'],
                    'Bounding boxes symbols': result['Bounding boxes symbols'],
                    'Bounding boxes words': result['Bounding boxes words'],
                    'Text rough recognized': result['Text rough recognized'],
                    'Text rough translated': result['Text rough translated'],
                    'Text corrected recognized': result['Text corrected recognized'],
                    'Text corrected translated': result['Text corrected translated']
                };
                updateDisplayedText();
                updateDisplayedImage();
                updateHints();
                saveBtn.disabled = false;
            } else {
                status.textContent = `Error: ${result.Error} - ${result['Error details'] || ''}`;
                console.error('Process error:', result);
                processBtn.disabled = false;
            }
        } catch (error) {
            status.textContent = `Error: ${error.message}`;
            console.error('Fetch error:', error);
            processBtn.disabled = false;
        }
        processBtn.disabled = false;
    });

    // Save Button: Download processed files and text
    saveBtn.addEventListener('click', async () => {
        if (!processedData) {
            status.textContent = 'Error: No processed data available.';
            return;
        }

        try {
            status.textContent = 'Preparing download...';
            const zip = new JSZip();

            // Получаем имя файла и расширение (если они есть)
            const originalUrl = processedData['Image boxed symbols url'] || 
                               processedData['Image boxed words url'] || 
                               processedData['Image translated rough url'] || 
                               processedData['Image translated corrected url'];

            let name = 'output'; // значение по умолчанию
            let ext = 'png';     // значение по умолчанию (можно изменить)

            if (originalUrl) {
                const urlParts = originalUrl.split('/').pop().split('.');
                name = urlParts.slice(0, -1).join('.'); // имя без расширения
                ext = urlParts.pop();                   // расширение
            }

            // Добавляем изображения
            const imageUrls = {
                'image_boxed_symbols': processedData['Image boxed symbols url'],
                'image_boxed_words': processedData['Image boxed words url'],
                'image_translated_rough': processedData['Image translated rough url'],
                'image_translated_corrected': processedData['Image translated corrected url']
            };

            for (const [key, url] of Object.entries(imageUrls)) {
                if (!url) continue; // пропускаем, если URL нет
                const response = await fetch(url);
                if (response.ok) {
                    const blob = await response.blob();
                    zip.file(`${name}_${key}.${ext}`, blob);
                } else {
                    console.warn(`Failed to fetch ${key} image: HTTP ${response.status}`);
                }
            }

            // Добавляем текстовые файлы и JSON
            const textFiles = {
                'text_rough_recognized': processedData['Text rough recognized'],
                'text_rough_translated': processedData['Text rough translated'],
                'text_corrected_recognized': processedData['Text corrected recognized'],
                'text_corrected_translated': processedData['Text corrected translated']
            };

            for (const [key, content] of Object.entries(textFiles)) {
                if (content) {
                    zip.file(`${name}_${key}.txt`, content);
                }
            }

            // Добавляем JSON с bounding boxes
            const boundingBoxes = {
                'bounding_boxes_symbols': processedData['Bounding boxes symbols'],
                'bounding_boxes_words': processedData['Bounding boxes words']
            };

            for (const [key, content] of Object.entries(boundingBoxes)) {
                if (content) {
                    zip.file(`${name}_${key}.json`, content);
                }
            }

            // Генерируем и скачиваем ZIP
            const zipContent = await zip.generateAsync({ type: 'blob' });
            const zipUrl = URL.createObjectURL(zipContent);
            const downloadLink = document.createElement('a');
            downloadLink.href = zipUrl;
            downloadLink.download = `ScreenTranslator_${name}.zip`;
            downloadLink.click();
            URL.revokeObjectURL(zipUrl);

            status.textContent = 'Files saved successfully.';
        } catch (error) {
            status.textContent = `Error saving files: ${error.message}`;
            console.error('Save error:', error);
        }
    });
});