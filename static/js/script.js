document.addEventListener("DOMContentLoaded", function() {
    const alertElements = document.querySelectorAll('.alert-dismissible');

    if (alertElements.length > 0) {
        setTimeout(() => {
            alertElements.forEach(element => {
                const bsAlert = new bootstrap.Alert(element);
                bsAlert.close();
            });
        }, 3000);
    }

    const toggleBtn = document.getElementById('darkModeToggle');
    const htmlElement = document.documentElement;

    if (htmlElement.getAttribute('data-bs-theme') === 'dark') {
        toggleBtn.innerHTML = '☀️ Light';
    }

    toggleBtn.addEventListener('click', () => {
        const currentTheme = htmlElement.getAttribute('data-bs-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        
        htmlElement.setAttribute('data-bs-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        
        toggleBtn.innerHTML = newTheme === 'dark' ? '☀️ Light' : '🌙 Dark';
    });
});