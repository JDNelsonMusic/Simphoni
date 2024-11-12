// app/static/js/trivia.js

document.addEventListener('DOMContentLoaded', () => {
    const timerElement = document.createElement('p');
    timerElement.id = 'timer';
    timerElement.classList.add('mt-3', 'text-end', 'text-muted');
    document.querySelector('.card-body').prepend(timerElement);

    let timeLeft = 30; // 30 seconds for each question

    const countdown = setInterval(() => {
        if (timeLeft <= 0) {
            clearInterval(countdown);
            timerElement.textContent = 'Time is up!';
            document.querySelector('form').submit(); // Automatically submit the form
        } else {
            timerElement.textContent = `Time left: ${timeLeft} seconds`;
        }
        timeLeft -= 1;
    }, 1000);
});
