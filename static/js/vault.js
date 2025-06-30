/**
 * Password Vault JavaScript
 * Handles all interactions for the password vault page including search
 */

document.addEventListener('DOMContentLoaded', () => {
    // Initialize clipboard.js for copy buttons
    if (typeof ClipboardJS !== 'undefined') {
        new ClipboardJS('.copy-btn').on('success', function(e) {
            const btn = e.trigger;
            const originalIcon = btn.innerHTML;
            btn.innerHTML = '<i class="fas fa-check text-success"></i>';
            
            setTimeout(() => {
                btn.innerHTML = originalIcon;
            }, 1500);
            
            e.clearSelection();
        });
    }

    // Search functionality
    const searchInput = document.getElementById('vaultSearch');
    const clearSearchBtn = document.getElementById('clearSearch');
    const clearSearchLink = document.getElementById('clearSearchBtn');
    const searchResultsInfo = document.getElementById('searchResultsInfo');
    const noSearchResults = document.getElementById('noSearchResults');
    const vaultGrid = document.getElementById('vaultGrid');
    
    if (searchInput) {
        let searchTimeout;
        
        // Search input handler with debouncing
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                performSearch(this.value.trim());
            }, 300);
            
            // Show/hide clear button
            if (this.value.length > 0) {
                clearSearchBtn.classList.add('show');
            } else {
                clearSearchBtn.classList.remove('show');
            }
        });
        
        // Clear search functionality
        function clearSearch() {
            searchInput.value = '';
            clearSearchBtn.classList.remove('show');
            performSearch('');
        }
        
        clearSearchBtn.addEventListener('click', clearSearch);
        if (clearSearchLink) {
            clearSearchLink.addEventListener('click', clearSearch);
        }
        
        // Perform the actual search
        function performSearch(query) {
            const cards = document.querySelectorAll('.vault-entry-card');
            let visibleCount = 0;
            
            if (query === '') {
                // Show all cards
                cards.forEach(card => {
                    card.classList.remove('hidden');
                    visibleCount++;
                });
                searchResultsInfo.style.display = 'none';
                noSearchResults.classList.remove('show');
            } else {
                // Filter cards based on search query
                const searchTerm = query.toLowerCase();
                
                cards.forEach(card => {
                    const siteName = card.querySelector('.site-name')?.textContent?.toLowerCase() || '';
                    const siteUrl = card.querySelector('.site-url')?.textContent?.toLowerCase() || '';
                    const username = card.querySelector('.credential-text')?.textContent?.toLowerCase() || '';
                    
                    const matches = siteName.includes(searchTerm) || 
                                  siteUrl.includes(searchTerm) || 
                                  username.includes(searchTerm);
                    
                    if (matches) {
                        card.classList.remove('hidden');
                        visibleCount++;
                    } else {
                        card.classList.add('hidden');
                    }
                });
                
                // Update search results info
                if (visibleCount > 0) {
                    searchResultsInfo.textContent = `Found ${visibleCount} result${visibleCount !== 1 ? 's' : ''} for "${query}"`;
                    searchResultsInfo.style.display = 'block';
                    noSearchResults.classList.remove('show');
                } else {
                    searchResultsInfo.style.display = 'none';
                    noSearchResults.classList.add('show');
                }
            }
        }
        
        // Handle Enter key to prevent form submission
        searchInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                performSearch(this.value.trim());
            }
        });
    }

    // Toggle password visibility with enhanced layout stabilization
    document.querySelectorAll('.toggle-password-btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            const card = this.closest('.vault-entry-card');
            const passwordField = card.querySelector('.password-field');
            const actualPassword = card.querySelector('.actual-password');
            const icon = this.querySelector('i');
            
            // Prevent any layout shifts by maintaining container dimensions
            const container = document.querySelector('.vault-container');
            const containerRect = container.getBoundingClientRect();
            
            // Lock container dimensions temporarily
            container.style.minHeight = containerRect.height + 'px';
            container.style.width = containerRect.width + 'px';
            
            if (passwordField.textContent === '••••••••') {
                passwordField.textContent = actualPassword.textContent;
                icon.classList.replace('fa-eye', 'fa-eye-slash');
                
                // Auto-hide after 10 seconds
                setTimeout(() => {
                    if (passwordField.textContent !== '••••••••') {
                        passwordField.textContent = '••••••••';
                        icon.classList.replace('fa-eye-slash', 'fa-eye');
                    }
                }, 10000);
            } else {
                passwordField.textContent = '••••••••';
                icon.classList.replace('fa-eye-slash', 'fa-eye');
            }
            
            // Release container lock after a brief moment
            setTimeout(() => {
                container.style.minHeight = '';
                container.style.width = '';
            }, 300);
        });
    });
    
    // Layout stabilization for vault cards
    function stabilizeLayout() {
        // Prevent layout shifts during mouse movements
        const vaultContainer = document.querySelector('.vault-container');
        if (vaultContainer) {
            let isStable = true;
            
            vaultContainer.addEventListener('mousemove', (e) => {
                if (!isStable) return;
                
                // Throttle mousemove events to prevent excessive recalculations
                isStable = false;
                setTimeout(() => {
                    isStable = true;
                }, 16); // ~60fps
            });
            
            // Lock dimensions on mouseenter to prevent shifts
            document.querySelectorAll('.vault-entry-card').forEach(card => {
                card.addEventListener('mouseenter', () => {
                    const rect = card.getBoundingClientRect();
                    card.style.minHeight = rect.height + 'px';
                    card.style.minWidth = rect.width + 'px';
                });
                
                card.addEventListener('mouseleave', () => {
                    setTimeout(() => {
                        card.style.minHeight = '';
                        card.style.minWidth = '';
                    }, 300);
                });
            });
        }
    }
    
    // Initialize layout stabilization
    stabilizeLayout();
    
    // Additional stability measures
    window.addEventListener('resize', () => {
        // Re-stabilize on window resize
        setTimeout(stabilizeLayout, 100);
    });
});
