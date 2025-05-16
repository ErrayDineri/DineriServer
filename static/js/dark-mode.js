// Dark Mode Toggle functionality - optimized version
document.addEventListener('DOMContentLoaded', function() {
    // Remove preload class to enable transitions
    document.documentElement.classList.remove('dark-mode-preload');
    
    const darkModeToggle = document.getElementById('darkModeToggle');
    const body = document.body;
    
    if (!darkModeToggle) return;
    
    // Optimize toggle with debounce to avoid multiple rapid toggles
    let toggleTimeout;
    darkModeToggle.addEventListener('click', function () {
        clearTimeout(toggleTimeout);
        toggleTimeout = setTimeout(() => {
            body.classList.toggle('dark-mode');
            darkModeToggle.textContent = body.classList.contains('dark-mode') ? '🌞' : '🌙';
            
            // Save preference to localStorage
            localStorage.setItem('darkMode', body.classList.contains('dark-mode'));
        }, 10); // Small delay to prevent multiple rapid toggles
    });
    
    // Check if user has a saved preference
    const savedDarkMode = localStorage.getItem('darkMode');
    if (savedDarkMode === 'true') {
        body.classList.add('dark-mode');
        const cards = document.querySelectorAll('.glass-card');
        cards.forEach(card => card.classList.add('dark-mode'));
        darkModeToggle.textContent = '🌞';
    }
});
