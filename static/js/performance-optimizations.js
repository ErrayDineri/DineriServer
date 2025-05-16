// Performance improvements for Dineri Server

document.addEventListener('DOMContentLoaded', function() {
  // Check for performance mode preference
  const isPerformanceMode = localStorage.getItem('performanceMode') === 'true';
  
  // Apply performance mode if enabled
  if (isPerformanceMode) {
    document.body.classList.add('reduced-motion');
  }
  
  // Initialize the performance button
  createPerformanceButton(isPerformanceMode);
  
  // Set up performance monitoring
  setupPerformanceObserver();
  
  // Apply optimizations for all pages
  applyGlobalOptimizations();
  
  // Listen for system preference changes
  listenForSystemPreferences();
});

/**
 * Creates a toggle button for performance mode
 */
function createPerformanceButton(isEnabled) {
  const navbar = document.querySelector('.navbar-nav');
  if (!navbar) return;
  
  const performanceItem = document.createElement('li');
  performanceItem.className = 'nav-item';
  
  const button = document.createElement('button');
  button.className = 'btn btn-sm btn-outline-secondary nav-link ms-2';
  button.id = 'performanceToggle';
  button.textContent = isEnabled ? '🚀 Enable Animations' : '⚡ Performance Mode';
  
  button.addEventListener('click', function() {
    const currentSetting = document.body.classList.toggle('reduced-motion');
    localStorage.setItem('performanceMode', currentSetting);
    this.textContent = currentSetting ? '🚀 Enable Animations' : '⚡ Performance Mode';
  });
  
  performanceItem.appendChild(button);
  navbar.appendChild(performanceItem);
}

/**
 * Set up performance monitoring
 */
function setupPerformanceObserver() {
  // Monitor rendering performance
  if ('PerformanceObserver' in window) {
    try {
      const observer = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          // If any layout shifts are too large, enable performance mode
          if (entry.entryType === 'layout-shift' && entry.value > 0.5) {
            console.log('Large layout shift detected, enabling performance mode');
            document.body.classList.add('reduced-motion');
          }
        }
      });
      
      observer.observe({ entryTypes: ['layout-shift', 'largest-contentful-paint'] });
    } catch (e) {
      console.log('Performance observer not supported in this browser');
    }
  }
}

/**
 * Apply global optimizations for all pages
 */
function applyGlobalOptimizations() {
  // Add hardware acceleration to all animated elements
  document.querySelectorAll('.fade-in, .slide-in-left, .slide-in-right, .zoom-in')
    .forEach(el => {
      el.style.willChange = 'transform, opacity';
      el.style.backfaceVisibility = 'hidden';
    });
  
  // Optimize scrolling
  document.querySelectorAll('[id^="scrollArea"]').forEach(el => {
    el.style.webkitOverflowScrolling = 'touch';
  });
  
  // Optimize image loading
  document.querySelectorAll('img').forEach(img => {
    img.loading = 'lazy';
  });
}

/**
 * Listen for system preferences changes
 */
function listenForSystemPreferences() {
  if (window.matchMedia) {
    const prefersDarkQuery = window.matchMedia('(prefers-color-scheme: dark)');
    const prefersReducedMotionQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    
    // Handle dark mode preference
    prefersDarkQuery.addEventListener('change', event => {
      if (localStorage.getItem('darkMode') === null) {
        // Only auto-switch if user hasn't set a preference
        document.body.classList.toggle('dark-mode', event.matches);
      }
    });
    
    // Handle reduced motion preference
    prefersReducedMotionQuery.addEventListener('change', event => {
      if (localStorage.getItem('performanceMode') === null) {
        // Only auto-switch if user hasn't set a preference
        document.body.classList.toggle('reduced-motion', event.matches);
      }
    });
    
    // Apply reduced motion if system prefers it and user hasn't set a preference
    if (prefersReducedMotionQuery.matches && localStorage.getItem('performanceMode') === null) {
      document.body.classList.add('reduced-motion');
    }
  }
}
