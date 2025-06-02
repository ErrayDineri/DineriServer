// Initialize Video.js player with custom options
document.addEventListener('DOMContentLoaded', function() {
  // Initialize Video.js player with custom options
  const player = videojs('video-player', {
    controlBar: {
      children: [
        'playToggle',
        'volumePanel',
        'currentTimeDisplay',
        'timeDivider',
        'durationDisplay',
        'progressControl',
        'playbackRateMenuButton',
        'fullscreenToggle'
      ]
    }
  });
  
  // Check if we're in dark mode and apply appropriate styling
  if (document.body.classList.contains('dark-mode')) {
    document.querySelector('.video-js').classList.add('dark-mode');
  }
  
  // Listen for dark mode changes
  document.addEventListener('dark-mode-changed', function(e) {
    if (e.detail.darkMode) {
      document.querySelector('.video-js').classList.add('dark-mode');
    } else {
      document.querySelector('.video-js').classList.remove('dark-mode');
    }
  });
});
