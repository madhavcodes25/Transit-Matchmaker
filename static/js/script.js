document.addEventListener("DOMContentLoaded", function () {

    /* ── Theme Toggle ── */
    const toggleBtn   = document.getElementById('darkModeToggle');
    const htmlEl      = document.documentElement;
    const moonIcon    = document.getElementById('theme-icon-moon');
    const sunIcon     = document.getElementById('theme-icon-sun');

    function applyThemeIcons(theme) {
        if (theme === 'dark') {
            moonIcon.style.display = 'none';
            sunIcon.style.display  = 'block';
        } else {
            moonIcon.style.display = 'block';
            sunIcon.style.display  = 'none';
        }
    }

    // Apply correct icon on load
    applyThemeIcons(htmlEl.getAttribute('data-bs-theme'));

    toggleBtn.addEventListener('click', () => {
        const current  = htmlEl.getAttribute('data-bs-theme');
        const next     = current === 'dark' ? 'light' : 'dark';
        htmlEl.setAttribute('data-bs-theme', next);
        localStorage.setItem('theme', next);
        applyThemeIcons(next);
    });

    /* ── Auto-dismiss flash messages ── */
    const flashes = document.querySelectorAll('.flash');
    if (flashes.length > 0) {
        setTimeout(() => {
            flashes.forEach(el => {
                el.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
                el.style.opacity = '0';
                el.style.transform = 'translateY(-6px)';
                setTimeout(() => el.remove(), 300);
            });
        }, 4000);
    }

});