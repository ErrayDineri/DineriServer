// Performance settings toggle

document.addEventListener('DOMContentLoaded', function() {
  // Check for saved performance setting
  const reducedMotion = localStorage.getItem('reducedMotion') === 'true';
  
  // Apply setting
  if (reducedMotion) {
    document.body.classList.add('reduced-motion');
  }
  
  // Add toggle next to dark mode toggle
  const darkModeToggle = document.getElementById('darkModeToggle');
  if (darkModeToggle && darkModeToggle.parentNode) {
    // Create the performance toggle button with the same styling as dark mode toggle
    const perfToggle = document.createElement('button');
    perfToggle.className = darkModeToggle.className; // Same classes as dark mode toggle
    perfToggle.id = 'performanceToggle';
    perfToggle.innerHTML = reducedMotion ? '🚀' : '⚡';
    
    // Set tooltip title
    perfToggle.title = reducedMotion ? 'Enable Animations' : 'Performance Mode';
    
    // Insert right after dark mode toggle
    darkModeToggle.parentNode.insertBefore(perfToggle, darkModeToggle.nextSibling);
    
    // Add toggle functionality
    perfToggle.addEventListener('click', function() {
      const currentSetting = document.body.classList.toggle('reduced-motion');
      localStorage.setItem('reducedMotion', currentSetting);
      this.innerHTML = currentSetting ? '🚀' : '⚡';
      this.title = currentSetting ? 'Enable Animations' : 'Performance Mode';
    });
  }
});
