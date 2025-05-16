// Dropdown fix for Bootstrap 5
document.addEventListener('DOMContentLoaded', function() {
    // Fix for source filter dropdown
    const sourceDropdown = document.getElementById('sourceFilterDropdown');
    if (sourceDropdown) {
        // Initialize dropdown with specific options
        const dropdown = new bootstrap.Dropdown(sourceDropdown, {
            boundary: document.querySelector('body'),
            reference: 'toggle',
            display: 'dynamic'
        });
        
        // Ensure dropdown is always on top when shown
        sourceDropdown.addEventListener('shown.bs.dropdown', function() {
            const menu = document.getElementById('sourceFilterMenu');
            if (menu) {
                // Force it to the top level of the DOM for proper z-index
                document.body.appendChild(menu);
                
                // Position it correctly relative to the button
                const buttonRect = sourceDropdown.getBoundingClientRect();
                menu.style.position = 'fixed';
                menu.style.top = (buttonRect.bottom + window.scrollY) + 'px';
                menu.style.left = (buttonRect.left + window.scrollX) + 'px';
                menu.style.zIndex = '9999';
                menu.style.width = 'auto';
                menu.style.minWidth = buttonRect.width + 'px';
            }
        });
        
        // Put it back in the right place when hidden
        sourceDropdown.addEventListener('hidden.bs.dropdown', function() {
            const menu = document.getElementById('sourceFilterMenu');
            if (menu && menu.parentNode === document.body) {
                document.querySelector('.dropdown').appendChild(menu);
            }
        });
    }
});
