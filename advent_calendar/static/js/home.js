let isStarUnlocked = false;

// Update window.onload function
window.onload = async function() {
    // Only create calendar if user is authenticated
    if (typeof currentConfig !== 'undefined') {
        const calendar = document.getElementById('calendar');
        if (calendar) {
            createCalendar();
            await checkStarStatus();
        }
    }

    // Add click event listener for close button
    document.addEventListener('click', function(event) {
        if (event.target.classList.contains('close-star')) {
            closeStarMessage(event);
        }
    });

    // Add click event listener for star
    const star = document.querySelector('.tree-star');
    if (star) {
        star.addEventListener('click', handleStarClick);
    }

    // Add enter key support for both password inputs
    document.addEventListener('keypress', function(event) {
        if (event.key === 'Enter') {
            const activeElement = document.activeElement;
            if (activeElement.type === 'password') {
                event.preventDefault();
                checkPassword();
            }
        }
    });
};

// Check star status
async function checkStarStatus() {
    try {
        const response = await fetch('/is_star_unlocked');
        const data = await response.json();
        isStarUnlocked = data.unlocked;
    } catch (error) {
        console.error('Error checking star status:', error);
    }
}

// Handle star click
async function handleStarClick() {
    const star = document.querySelector('.tree-star');
    let promptDiv = document.querySelector('.password-prompt');

    if (isStarUnlocked) {
        star.classList.add('expanded');
        return;
    }

    if (!promptDiv) {
        promptDiv = document.createElement('div');
        promptDiv.className = 'password-prompt';
        promptDiv.innerHTML = `
            <p>Pinsoft ❤️</p>
            <input type="password" id="starPasswordInput">
            <button onclick="checkPassword()">Submit</button>
        `;
        document.body.appendChild(promptDiv);
    } else {
        promptDiv.style.display = promptDiv.style.display === 'none' ? 'block' : 'none';
        if (promptDiv.style.display === 'block') {
            const input = promptDiv.querySelector('input');
            input.value = '';
            input.focus();
        }
    }
}

// Password checking function
function checkPassword() {
    const activeInput = document.activeElement;
    if (!activeInput || activeInput.type !== 'password') return;

    const formData = new FormData();
    formData.append('password', activeInput.value);

    const endpoint = activeInput.id === 'passwordInput'
        ? '/check_unlock_password'
        : '/check_star_password';

    fetch(endpoint, {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            if (activeInput.id === 'passwordInput') {
                window.location.reload();
            } else {
                const promptDiv = activeInput.closest('.password-prompt');
                const star = document.querySelector('.tree-star');

                promptDiv.style.display = 'none';
                activeInput.value = '';
                star.classList.add('expanded');
                isStarUnlocked = true;
            }
        } else {
            activeInput.value = '';
            activeInput.placeholder = 'Try again...';
            if (activeInput.id === 'passwordInput') {
                showError();
            }
        }
    })
    .catch(error => {
        console.error('Error:', error);
        activeInput.value = '';
        activeInput.placeholder = 'Error occurred...';
    });
}

function showError() {
    const errorContainer = document.getElementById('errorContainer');
    if (errorContainer) {
        errorContainer.style.display = 'block';
        setTimeout(() => {
            errorContainer.style.display = 'none';
        }, 3000);
    }
}

function createCalendar() {
    const calendar = document.getElementById('calendar');
    if (!calendar) return;

    calendar.innerHTML = '';

    const heartContainer = document.createElement('div');
    heartContainer.className = 'heart-container';

    const layout = [
        [0, 1, 2, 0, 3, 4, 0],
        [5, 6, 7, 8, 9, 10, 11],
        [12, 13, 14, 15, 16, 17, 18],
        [0, 19, 20, 21, 22, 23, 0],
        [0, 0, 24, 25, 26, 0, 0],
        [0, 0, 0, 27, 0, 0, 0]
    ];

    layout.forEach(row => {
        const rowDiv = document.createElement('div');
        rowDiv.className = 'heart-row';

        row.forEach(boxNum => {
            if (boxNum === 0) {
                const spacer = document.createElement('div');
                spacer.className = 'heart-spacer';
                rowDiv.appendChild(spacer);
            } else {
                const box = createBox(boxNum);
                box.className += ' heart-box';
                rowDiv.appendChild(box);
            }
        });

        heartContainer.appendChild(rowDiv);
    });

    calendar.appendChild(heartContainer);
}

function createBox(number) {
    const box = document.createElement('div');
    box.className = 'calendar-box';
    box.setAttribute('data-box-number', number);

    const content = document.createElement('div');
    content.className = 'box-content';

    const heart = document.createElement('div');
    heart.className = 'gift-emoji';
    heart.textContent = '🥰';
    content.appendChild(heart);

    const imageUrl = currentConfig[number]?.image;
    if (imageUrl && imageUrl !== String(number)) {
        const imgContainer = document.createElement('div');
        imgContainer.className = 'image-container';
        imgContainer.style.display = 'none';

        const img = document.createElement('img');
        img.src = imageUrl;
        img.alt = `Box ${number}`;
        imgContainer.appendChild(img);
        content.appendChild(imgContainer);
    }

    box.appendChild(content);
    box.onclick = () => handleBoxClick(box);
    return box;
}

function handleBoxClick(element) {
    if (!element.classList.contains('opened')) {
        element.classList.add('opened');
        createSparkles(element);

        const giftEmoji = element.querySelector('.gift-emoji');
        const imageContainer = element.querySelector('.image-container');

        if (giftEmoji) {
            giftEmoji.style.display = 'none';
        }

        if (imageContainer) {
            imageContainer.style.display = 'block';
        }
    }
}

function createSparkles(element) {
    for (let i = 0; i < 12; i++) {
        const sparkle = document.createElement('div');
        sparkle.className = 'sparkle';
        sparkle.style.left = Math.random() * 100 + '%';
        sparkle.style.top = Math.random() * 100 + '%';
        sparkle.style.animation = 'sparkle 0.8s ease-in-out';
        sparkle.style.animationDelay = (i * 0.1) + 's';
        element.appendChild(sparkle);
        setTimeout(() => sparkle.remove(), 1000);
    }
}

function closeStarMessage(event) {
    event.stopPropagation();

    const star = document.querySelector('.tree-star');
    const promptDiv = document.querySelector('.password-prompt');

    star.style.transition = 'all 0.3s ease';
    star.classList.remove('expanded');

    if (promptDiv && promptDiv.style.display !== 'none') {
        promptDiv.style.display = 'none';
        const input = promptDiv.querySelector('input');
        if (input) {
            input.value = '';
        }
    }
}