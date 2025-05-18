document.addEventListener('DOMContentLoaded', () => {
    const uploadInput = document.getElementById('upload');
    const uploadBtn = document.getElementById('upload-btn');
    const processBtn = document.getElementById('process-btn');
    const saveBtn = document.getElementById('save-btn');
    const originalImage = document.getElementById('original-image');
    const originalVideo = document.getElementById('original-video');
    const processedImage = document.getElementById('processed-image');
    const processedVideo = document.getElementById('processed-video');
    const recognizedText = document.getElementById('recognized-text');
    const translatedText = document.getElementById('translated-text');
    const status = document.getElementById('status');
    const paramsForm = document.getElementById('params-form');

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
    let processedFilename = null;

    // Upload Button: Trigger file input and validate
    uploadBtn.addEventListener('click', () => uploadInput.click());

    uploadInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (!file) {
            status.textContent = 'Error: No file selected.';
            return;
        }

        // Validate file type and size
        const ext = file.name.split('.').pop().toLowerCase();
        if (!ALLOWED_EXTENSIONS.includes(ext)) {
            status.textContent = `Error: Unsupported file type. Use ${IMAGE_EXTENSIONS.join(', ')} for images or ${VIDEO_EXTENSIONS.join(', ')} for videos.`;
            uploadInput.value = '';
            return;
        }
        if (file.size > MAX_FILE_SIZE) {
            status.textContent = 'Error: File size exceeds 10MB.';
            uploadInput.value = '';
            return;
        }

        currentFile = file;
        processBtn.disabled = false;
        saveBtn.disabled = true;
        status.textContent = 'File selected. Click "Process" to start.';

        // Preview original media
        const url = URL.createObjectURL(file);
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
        recognizedText.value = '';
        translatedText.value = '';

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
            rough_text_recognition: formData.get('rough_text_recognition') === 'on',
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
            const response = await fetch('/ScreenTranslatorAPI/process', {
                method: 'POST',
                body: uploadFormData,
            });
            const result = await response.json();
            console.log('Process response:', result); // Debug log

            if (response.ok) {
                status.textContent = 'Processing complete.';
                processedFilename = result.filename; // Use backend-provided filename
                console.log('Using filename:', processedFilename); // Debug log
                const url = result.boxed_url; // Use boxed_url from response
                console.log('Fetching boxed_url:', url); // Debug log
                const ext = processedFilename.split('.').pop().toLowerCase();
                if (IMAGE_EXTENSIONS.includes(ext)) {
                    processedImage.src = url;
                    processedImage.style.display = 'block';
                    processedVideo.style.display = 'none';
                } else if (VIDEO_EXTENSIONS.includes(ext)) {
                    processedVideo.src = url;
                    processedVideo.style.display = 'block';
                    processedImage.style.display = 'none';
                }
                recognizedText.value = result.recognized_text || '';

                // Try fetching translated text (if available)
                translatedText.value = result.translated_text || '';
                saveBtn.disabled = false;
            } else {
                status.textContent = `Error: ${result.error} - ${result.details || ''}`;
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

    // Save Button: Download processed file and text
    saveBtn.addEventListener('click', async () => {
        if (!processedFilename) {
            status.textContent = 'Error: No processed file available.';
            return;
        }

        try {
            status.textContent = 'Preparing download...';
            const zip = new JSZip();

            // Add processed file
            const boxedResponse = await fetch(`/ScreenTranslatorAPI/boxed/${processedFilename}`);
            if (boxedResponse.ok) {
                const blob = await boxedResponse.blob();
                zip.file(processedFilename, blob);
            } else {
                status.textContent = `Error: Processed file not found (HTTP ${boxedResponse.status})`;
                console.error('Boxed fetch error:', boxedResponse.statusText);
                return;
            }

            // Add translated file (if available)
            const translatedResponse = await fetch(`/ScreenTranslatorAPI/translated/${processedFilename}`);
            if (translatedResponse.ok) {
                const translatedBlob = await translatedResponse.blob();
                zip.file(`translated-${processedFilename}`, translatedBlob);
            } else {
                console.warn('Translated file not available:', translatedResponse.status);
            }

            // Add text files for recognized and translated text
            if (recognizedText.value) {
                zip.file('recognized_text.txt', recognizedText.value);
            }
            if (translatedText.value) {
                zip.file('translated_text.txt', translatedText.value);
            }

            const content = await zip.generateAsync({ type: 'blob' });
            const url = URL.createObjectURL(content);
            const a = document.createElement('a');
            a.href = url;
            a.download = `screen_translator_output_${Date.now()}.zip`;
            a.click();
            URL.revokeObjectURL(url);
            status.textContent = 'Files saved successfully.';
        } catch (error) {
            status.textContent = `Error saving files: ${error.message}`;
            console.error('Save error:', error);
        }
    });

    document.getElementById('footer-text').addEventListener('click', () => {
        window.open('/apidocs', '_blank');
    });
});