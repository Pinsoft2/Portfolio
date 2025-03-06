document.addEventListener('DOMContentLoaded', function() {
    const fileInput = document.querySelector('input[type="file"]');
    const fileLabel = document.querySelector('.file-label');
    const processButton = document.getElementById('process-doc');
    const previewText = document.querySelector('.preview-text');
    const addButton = document.getElementById('add');

    // Create file name display element
    const fileNameDisplay = document.createElement('div');
    fileNameDisplay.className = 'file-name';
    fileLabel.parentNode.appendChild(fileNameDisplay);

    function formatPreviewContent(content) {
        if (!content) return '';
        return content.split('\n')
            .map(para => para.trim())
            .filter(para => para.length > 0)
            .map(para => `<p>${para}</p>`)
            .join('');
    }

    // Word pair addition
    addButton.addEventListener('click', function() {
        const wordPairDiv = document.createElement('div');
        wordPairDiv.className = 'word-pair';
        wordPairDiv.innerHTML = `
            <input type="text" name="old_word" placeholder="Word to replace">
            <input type="text" name="new_word" placeholder="New word">
        `;
        document.getElementById('data_table').appendChild(wordPairDiv);
    });

    // File input handling
    fileInput.addEventListener('change', function(e) {
        if (e.target.files.length > 0) {
            const file = e.target.files[0];
            // Update file name display
            fileNameDisplay.textContent = `Selected: ${file.name}`;
            fileNameDisplay.style.display = 'block';

            const formData = new FormData();
            formData.append('document', file);
            formData.append('action', 'Upload & Replace');

            previewText.textContent = 'Loading preview...';
            previewText.classList.add('processing');

            fetch(window.location.pathname, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => {
                if (!response.ok) throw new Error('Network response was not ok');
                return response.json();
            })
            .then(data => {
                previewText.classList.remove('processing');
                if (data.original_preview) {
                    previewText.innerHTML = `
                        <div class="preview-column">
                            <h3>Original Document</h3>
                            ${formatPreviewContent(data.original_preview)}
                        </div>
                    `;
                    processButton.style.display = 'block';
                } else {
                    previewText.textContent = 'No preview available';
                }
            })
            .catch(error => {
                console.error('Error:', error);
                previewText.textContent = 'Error loading preview. Please try again.';
                previewText.style.color = '#ff0000';
            });
        } else {
            fileNameDisplay.style.display = 'none';
            processButton.style.display = 'none';
        }
    });

    // Process button handling
    processButton.addEventListener('click', function(e) {
        e.preventDefault();

        const form = document.querySelector('form[name="Doc_form"]');
        if (form) {
            const formData = new FormData(form);
            formData.set('action', 'Upload & Replace');

            previewText.textContent = 'Processing...';
            previewText.classList.add('processing');

            fetch(window.location.pathname, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => {
                if (!response.ok) throw new Error('Network response was not ok');
                return response.json();
            })
            .then(data => {
                // Show both original and modified content side by side
                if (previewText) {
                    previewText.classList.remove('processing');

                    if (data.original_preview && data.modified_preview) {
                        previewText.innerHTML = `
                            <div class="preview-comparison">
                                <div class="preview-column">
                                    <h3>Original Document</h3>
                                    ${formatPreviewContent(data.original_preview)}
                                </div>
                                <div class="preview-column">
                                    <h3>Modified Document</h3>
                                    ${formatPreviewContent(data.modified_preview)}
                                </div>
                            </div>
                        `;
                        previewText.style.color = '#333';
                    } else {
                        previewText.textContent = 'No preview content available';
                        previewText.style.color = '#ff75e6';
                    }
                }
            })
            .catch(error => {
                console.error('Error:', error);
                previewText.textContent = 'Error processing document. Please try again.';
                previewText.style.color = '#ff0000';
                previewText.classList.remove('processing');
            });
        }
    });

    // Handle Enter key in input fields
    document.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && e.target.matches('input[type="text"]')) {
            e.preventDefault(); // Prevent form submission
        }
    });
});