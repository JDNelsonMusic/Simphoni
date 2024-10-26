// app/static/js/scripts.js

// Smooth scrolling for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const targetElement = document.querySelector(this.getAttribute('href'));
        if(targetElement){
            targetElement.scrollIntoView({
                behavior: 'smooth'
            });
        }
    });
});

// Drag-and-Drop Functionality for Available Functions and Model Order
document.addEventListener('DOMContentLoaded', () => {
    // Already implemented in setup.html and conversation.html
    // Additional global scripts can be added here
});

// Example: Toggle Dark Mode (if applicable)
const toggleDarkModeBtn = document.getElementById('toggle-dark-mode');
if(toggleDarkModeBtn){
    toggleDarkModeBtn.addEventListener('click', () => {
        document.body.classList.toggle('dark-mode');
        // Save user preference to localStorage or send to server
    });
}

// Example: Real-Time Notifications using WebSockets (optional)
if ('WebSocket' in window) {
    const ws = new WebSocket('ws://' + window.location.host + '/ws/notifications');

    ws.onmessage = function(event) {
        const data = JSON.parse(event.data);
        displayNotification(data.message, data.category);
    };

    ws.onclose = function() {
        console.log('WebSocket connection closed.');
    };
}

function displayNotification(message, category='info') {
    const notificationContainer = document.getElementById('notification-container');
    if(notificationContainer){
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${category} alert-dismissible fade show`;
        alertDiv.role = 'alert';
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        notificationContainer.appendChild(alertDiv);
    }
}

// Example: Form Validation Feedback
const forms = document.querySelectorAll('.needs-validation');
Array.from(forms).forEach(form => {
    form.addEventListener('submit', event => {
        if (!form.checkValidity()) {
            event.preventDefault();
            event.stopPropagation();
            form.classList.add('was-validated');
        }
    }, false);
});
