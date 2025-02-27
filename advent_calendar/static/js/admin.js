let currentConfig = {{ calendar_config|tojson|safe }};
function createConfigGrid() {
    console.log('Starting createConfigGrid');
    const grid = document.getElementById('configGrid');
    console.log('Found grid element:', grid);
    grid.innerHTML = '';

    const layout = [
        [0, 1, 2, 0, 3, 4, 0],
        [5, 6, 7, 8, 9, 10, 11],
        [12, 13, 14, 15, 16, 17, 18],
        [0, 19, 20, 21, 22, 23, 0],
        [0, 0, 24, 25, 26, 0, 0],
        [0, 0, 0, 27, 0, 0, 0]
    ];

    layout.forEach((row, rowIndex) => {
        const rowDiv = document.createElement('div');
        rowDiv.className = 'heart-row';

        row.forEach((boxNum, cellIndex) => {
            if (boxNum === 0) {
                const spacer = document.createElement('div');
                spacer.className = 'heart-spacer';
                spacer.style.width = '150px';
                rowDiv.appendChild(spacer);
            } else {
                const box = createConfigBox(boxNum);
                rowDiv.appendChild(box);
            }
        });

        grid.appendChild(rowDiv);
    });
}

function resetConfiguration() {
    if (confirm('Are you sure you want to reset all configurations?')) {
        // Clear all inputs
        document.querySelectorAll('.box-config input').forEach(input => {
            input.value = '';
        });
        // Clear all previews
        document.querySelectorAll('.preview-area').forEach(preview => {
            preview.textContent = preview.closest('.box-config').querySelector('.title').textContent.split(' ')[1];
        });
    }
}

function createConfigBox(number) {
    const box = document.createElement('div');
    box.className = 'box-config';

    const title = document.createElement('div');
    title.className = 'title';
    title.textContent = `Box ${number}`;
    box.appendChild(title);

    const urlInput = document.createElement('input');
    urlInput.type = 'text';
    urlInput.placeholder = 'Enter image URL';
    urlInput.setAttribute('data-box-number', number);
    urlInput.value = currentConfig[number]?.image || '';
    urlInput.onchange = (e) => handleImageUrl(e, number);
    box.appendChild(urlInput);

    const preview = document.createElement('div');
    preview.className = 'preview-area';
    if (currentConfig[number]?.image) {
        preview.innerHTML = `<img src="${currentConfig[number].image}" alt="Box ${number}">`;
    } else {
        preview.textContent = number;
    }
    box.appendChild(preview);

    return box;
}

async function handleImageUrl(event, boxNumber) {
    const imageUrl = event.target.value;
    const preview = event.target.nextElementSibling;

    try {
        const formData = new FormData();
        formData.append('box_number', boxNumber);
        formData.append('image_url', imageUrl);

        const response = await fetch('{{ url_for("save_box") }}', {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            currentConfig[boxNumber] = { image: imageUrl };
            preview.innerHTML = '';
            if (imageUrl) {
                preview.innerHTML = `<img src="${imageUrl}" alt="Box ${boxNumber}">`;
            } else {
                preview.textContent = boxNumber;
            }
            showNotification('Image URL saved successfully!');
        } else {
            throw new Error('Save failed');
        }
    } catch (error) {
        preview.textContent = boxNumber;
        showNotification('Failed to save image URL', true);
        console.error('Error:', error);
    }
}

async function saveAll() {
    const unlockPassword = document.getElementById('unlockPassword').value;
    const starPassword = document.getElementById('starPassword').value;

    try {
        const formData = new FormData();
        formData.append('unlock_password', unlockPassword);
        formData.append('star_password', starPassword);

        const response = await fetch('{{ url_for("save_settings") }}', {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            showNotification('All changes saved successfully!');
        } else {
            throw new Error('Save failed');
        }
    } catch (error) {
        showNotification('Failed to save changes', true);
        console.error('Save error:', error);
    }
}

function showNotification(message, isError = false) {
    const notification = document.getElementById('notification');
    notification.textContent = message;
    notification.style.background = isError ? '#dc2626' : '#065f46';
    notification.style.display = 'block';

    setTimeout(() => {
        notification.style.display = 'none';
    }, 3000);
}

document.addEventListener('DOMContentLoaded', function() {
    createConfigGrid();
});