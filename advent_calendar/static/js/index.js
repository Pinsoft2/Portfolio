const viewer = document.querySelector('spline-viewer');
const countdownElement = document.getElementById('countdown');
const instructionElement = document.getElementById('instruction');
let timeLeft = 10;
let countdownInterval;
let isMouseDown = false;

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
            window.location.href = '/home';
        }
    }, 1000);
}