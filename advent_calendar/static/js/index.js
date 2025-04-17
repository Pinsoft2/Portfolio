const viewer = document.querySelector('spline-viewer');
const countdownElement = document.getElementById('countdown');
const instructionElement = document.getElementById('instruction');
let timeLeft = 10;
let countdownInterval;
let isMouseDown = false;

// Function to get the base path - works in both environments
function getBasePath() {
    // Get the current path and check if it includes 'advent_calendar'
    const currentPath = window.location.pathname;
    if (currentPath.includes('/advent_calendar')) {
        return '/advent_calendar';
    }
    return '';
}

viewer.addEventListener('load', () => {
    console.log('Spline scene loaded');
    instructionElement.style.display = 'block';
});

document.addEventListener('mousedown', () => {
    isMouseDown = true;
});

document.addEventListener('mouseup', () => {
    if (isMouseDown && !countdownInterval) {
        startCountdown();
    }
    isMouseDown = false;
});

function startCountdown() {
    instructionElement.style.display = 'none';
    countdownElement.style.display = 'block';

    countdownInterval = setInterval(() => {
        countdownElement.textContent = timeLeft;
        timeLeft--;

        if (timeLeft < 0) {
            clearInterval(countdownInterval);
            // Use the base path function to determine the correct URL
            window.location.href = getBasePath() + '/home';
        }
    }, 1000);
}