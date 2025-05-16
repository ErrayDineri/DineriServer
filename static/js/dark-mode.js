// Dark Mode Toggle functionality
document.addEventListener('DOMContentLoaded', function() {
    const darkModeToggle = document.getElementById('darkModeToggle');
    const body = document.body;
    
    if (!darkModeToggle) return;
    
    darkModeToggle.addEventListener('click', function () {
        body.classList.toggle('dark-mode');
        const card = document.querySelector('.glass-card');
        if (card) card.classList.toggle('dark-mode');
        darkModeToggle.textContent = body.classList.contains('dark-mode') ? '🌞' : '🌙';
        
        // Save preference to localStorage
        localStorage.setItem('darkMode', body.classList.contains('dark-mode'));
    });
    
    // Check if user has a saved preference
    const savedDarkMode = localStorage.getItem('darkMode');
    if (savedDarkMode === 'true') {
        body.classList.add('dark-mode');
        const card = document.querySelector('.glass-card');
        if (card) card.classList.add('dark-mode');
        darkModeToggle.textContent = '🌞';
    }
});
