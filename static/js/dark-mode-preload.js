/* Prevent dark mode flash - optimized version */
(function() {
  // This script runs immediately before any other JS
  const prefersDarkMode = localStorage.getItem('darkMode') === 'true' || 
                         (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches && 
                          localStorage.getItem('darkMode') !== 'false');
  
  if (prefersDarkMode) {
    document.documentElement.classList.add('dark-mode-preload');
    
    // Optimized styles that apply immediately
    const style = document.createElement('style');
    style.textContent = `
      body { 
        background: linear-gradient(135deg, #121212, #1e1e1e, #2d2d2d) !important; 
        color: #f8f9fa !important;
        transition: none !important;
      }
      .glass-card { 
        background: rgba(0, 0, 0, 0.2) !important;
        transition: none !important;
      }
    `;    document.head.appendChild(style);
    
    // Remove the preload class as soon as possible
    document.addEventListener('DOMContentLoaded', () => {
      document.body.classList.add('dark-mode');
      
      // Use requestAnimationFrame for smoother transition
      requestAnimationFrame(() => {
        document.documentElement.classList.remove('dark-mode-preload');
        
        // Remove our temporary style after everything is loaded
        window.addEventListener('load', () => {
          style.remove();
        });
      });
    });
  }
})();
})();
