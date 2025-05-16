// Search functionality
let allResults = [],
    isLoading = false,
    sortAsc = false;
const selected = new Set();

/*–– UTILITY FUNCTIONS ––*/
function formatSize(sizeStr) {
    const [num, unit] = sizeStr.split(' ');
    const n = parseFloat(num) || 0;
    if (unit === 'GB') return n * 1024;
    if (unit === 'KB') return n / 1024;
    return n;
}

function renderRow(r) {
    const sel = selected.has(r.link) ? 'bg-info bg-opacity-75 text-dark' : '';
    const logo = `${STATIC_URL}sourceLogos/${r.source}.png`;
    return `
    <li class="p-2 mb-2 text-white border border-secondary rounded d-flex align-items-center ${sel} search-results-highlight stagger-item"
        data-link="${r.link}" style="cursor:pointer;">
      <img src="${logo}" width="24" class="me-2" alt="${r.source} logo"/>
      <div class="flex-grow-1" style="min-width: 0;">
        <h6 class="mb-1 text-truncate torrent-title" title="${r.title}">${r.title}</h6>
        <div class="d-flex justify-content-between">
          <small>${r.source} • ${r.size}</small>
          <small><i class="fas fa-arrow-up text-success"></i> ${r.seeders} <i class="fas fa-arrow-down text-danger ms-2"></i> ${r.leechers}</small>
        </div>
      </div>
    </li>`;
}

function getViewList() {
    const selectedSources = getSelectedSources();
    const allSelected = selectedSources.includes('all');
    const key = $('#sortBy').val();
    
    return allResults
        .filter(r => allSelected || selectedSources.includes(r.source))
        .sort((a, b) => {
            let va, vb;
            if (key === 'size') {
                va = formatSize(a.size);
                vb = formatSize(b.size);
            } else if (key === 'seeders' || key === 'leechers') {
                va = +a[key] || 0;
                vb = +b[key] || 0;
            } else {
                va = a.title.toLowerCase();
                vb = b.title.toLowerCase();
            }
            return sortAsc ? va - vb : vb - va;
        });
}

function fullRender() {
    const $c = $('#contentArea');
    $c.empty();
    const q = $('#searchQuery').val().trim();
    
    if (!q) {
        $('#downloadAllBtn').prop('disabled', true).text('⬇ Download All');
        return $c.append('<li class="text-center text-white p-4"><i class="fas fa-search fa-2x mb-3"></i><p>Type something to start searching</p></li>');
    }
    
    if (isLoading) {
        $('#downloadAllBtn').prop('disabled', true).text('⬇ Download All');
        return $c.append('<li class="text-center text-white p-4"><div class="spinner-border text-light mb-3" role="status"><span class="visually-hidden">Loading...</span></div><p>Searching for "' + q + '"...</p></li>');
    }
    
    // Performance optimization: Use DocumentFragment for batch DOM operations    const fragment = document.createDocumentFragment();
    
    if (!allResults.length) {
        $('#downloadAllBtn').prop('disabled', true).text('⬇ Download All');
        return $c.append('<li class="text-center text-white p-4"><i class="fas fa-exclamation-circle fa-2x mb-3"></i><p>No results found for "' + q + '"</p></li>');
    }
    
    const view = getViewList();
    if (!view.length) {
        $('#downloadAllBtn').prop('disabled', true).text('⬇ Download All');
        return $c.append('<li class="text-center text-white p-4"><i class="fas fa-filter fa-2x mb-3"></i><p>No matches with current filters</p></li>');
    }
    
    // Update download all button
    $('#downloadAllBtn').prop('disabled', false).text(`⬇ Download All (${view.length})`);
    
    // Performance optimization: Batch DOM insertions
    const tempDiv = document.createElement('div');
    const html = view.map(r => renderRow(r)).join('');
    tempDiv.innerHTML = html;
    
    // Add items to fragment
    while (tempDiv.firstChild) {
        fragment.appendChild(tempDiv.firstChild);
    }
      // Single DOM append for all elements
    $c[0].appendChild(fragment);
}

// Search with debounce for improved performance
let searchTimeout;
function doSearch() {
    const q = $('#searchQuery').val().trim();
    if (!q) return;
    
    // Clear any existing timeout
    clearTimeout(searchTimeout);
    
    // Set a short timeout to prevent multiple rapid searches
    searchTimeout = setTimeout(() => {
        // Show search in progress
        allResults = [];
        selected.clear();
        $('#bulkDownloadBtn').prop('disabled', true);
        isLoading = true;
        fullRender();
    
    // Add loading indicator to search button
    const $searchBtn = $('#searchBtn');
    const originalText = $searchBtn.html();
    $searchBtn.html('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>').prop('disabled', true);
    
    // Add animation to search container
    $('.search-container').addClass('border-primary');

    // Get selected sources
    const selectedSources = getSelectedSources();
    
    // Build URL with all selected sources
    let url = `/search/api/?query=${encodeURIComponent(q)}`;
    selectedSources.forEach(source => {
        url += `&filterSource=${encodeURIComponent(source)}`;
    });

    $.getJSON(url)
        .done(data => {
            allResults = data.results;
            
            // Highlight the search input for a moment to show success
            if (allResults.length > 0) {
                $('#searchQuery').addClass('border-success');
                setTimeout(() => $('#searchQuery').removeClass('border-success'), 1000);
            } else {
                $('#searchQuery').addClass('border-warning');
                setTimeout(() => $('#searchQuery').removeClass('border-warning'), 1000);
            }
        })
        .fail(() => {
            showAlert('❌ Search failed. Please try again.');
            $('#searchQuery').addClass('border-danger');
            setTimeout(() => $('#searchQuery').removeClass('border-danger'), 1000);
        })
        .always(() => {
            isLoading = false;
            $searchBtn.html(originalText).prop('disabled', false);
            $('.search-container').removeClass('border-primary');
            fullRender();
        });
}

function updateBulkBtn() {
    $('#bulkDownloadBtn').prop('disabled', !selected.size);
}

function getSelectedSources() {
    const sources = [];
    $('.source-filter-option:checked').each(function() {
        sources.push($(this).val());
    });
    return sources.length === 0 ? ['all'] : sources;
}

function updateSourceFilterDisplay() {
    const selectedSources = getSelectedSources();
    let buttonText = 'Sources';
    
    if (selectedSources.includes('all')) {
        buttonText = 'All Sources';
    } else if (selectedSources.length === 1) {
        buttonText = selectedSources[0];
    } else if (selectedSources.length > 1) {
        buttonText = `${selectedSources.length} Sources`;
    }
    
    $('#sourceFilterDropdown').text(buttonText);
    
    fullRender();
}

/*–– CUSTOM MODALS ––*/
function showAlert(msg, onClose) {
    const el = document.getElementById('alertModal');
    el.querySelector('#alertModalMessage').textContent = msg;
    const modal = new bootstrap.Modal(el);
    if (onClose) {
        el.addEventListener('hidden.bs.modal', function handler() {
            el.removeEventListener('hidden.bs.modal', handler);
            onClose();
        });
    }
    modal.show();
}

function showConfirm(msg, callback) {
    const el = document.getElementById('confirmModal');
    el.querySelector('#confirmModalMessage').textContent = msg;
    const modal = new bootstrap.Modal(el);

    // Clear previous handlers
    const okBtn = el.querySelector('#confirmBtn');
    const cancelBtn = el.querySelector('.btn-secondary');
    okBtn.replaceWith(okBtn.cloneNode(true));
    cancelBtn.replaceWith(cancelBtn.cloneNode(true));

    el.querySelector('#confirmBtn').addEventListener('click', () => {
        callback(true);
        modal.hide();
    });
    el.querySelector('.btn-secondary').addEventListener('click', () => {
        callback(false);
        modal.hide();
    });

    modal.show();
}

/*–– MAIN — EVENTS — INITIALIZE ––*/
$(function () {
    // Initialize download all button
    $('#downloadAllBtn').prop('disabled', true);
    
    // Search related variables
    let searchTimeout;
    const SEARCH_DELAY = 500; // ms to wait before auto-searching
    
    // Handle search input
    $('#searchQuery').on('input', function() {
        const query = $(this).val().trim();
        
        // Show/hide clear button based on input
        $('#clearSearchBtn').toggle(query.length > 0);
        
        // Clear any pending search timeout
        clearTimeout(searchTimeout);
        
        // Set a new timeout for search
        if (query.length >= 2) {
            searchTimeout = setTimeout(doSearch, SEARCH_DELAY);
        }
    });
    
    // Clear search button
    $('#clearSearchBtn').click(function() {
        $('#searchQuery').val('').focus();
        $(this).hide();
        allResults = [];
        selected.clear();
        updateBulkBtn();
        fullRender();
    });
    
    $('#sortDirBtn').click(() => {
        sortAsc = !sortAsc;
        $('#sortDirBtn').text(sortAsc ? '📈' : '📉');
        fullRender();
    });
    
    // Source filter handling
    $('#sourceAll').on('change', function() {
        if ($(this).is(':checked')) {
            // Uncheck other options but don't disable them
            $('.source-filter-option:not(#sourceAll)').prop('checked', false);
        }
        updateSourceFilterDisplay();
    });
    
    $('.source-filter-option:not(#sourceAll)').on('change', function() {
        if ($(this).is(':checked')) {
            // If any other source is checked, uncheck "All"
            $('#sourceAll').prop('checked', false);
        }
        
        // If no sources are selected, check "All"
        if ($('.source-filter-option:checked').length === 0) {
            $('#sourceAll').prop('checked', true);
        }
        
        updateSourceFilterDisplay();
    });
    
    // Sort By handling
    $('#sortBy').change(fullRender);
    
    // Search button click
    $('#searchBtn').click(function(e) {
        e.preventDefault();
        doSearch();
    });
    
    // Enter key in search input
    $('#searchQuery').keydown(function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            doSearch();
        }
        
        // Escape key clears search
        if (e.key === 'Escape') {
            e.preventDefault();
            $('#clearSearchBtn').click();
        }
    });
    
    // Download All button click
    $('#downloadAllBtn').click(function() {
        const currentResults = getViewList();
        if (!currentResults.length) {
            showAlert('⚠️ No torrents to download. Try searching first.');
            return;
        }
        
        showConfirm(`Are you sure you want to download all ${currentResults.length} currently visible torrents?`, ok => {
            if (!ok) return;
            
            const torrents = currentResults.map(r => ({
                link: r.link
            }));
            
            $.ajax({
                url: '/search/download/',
                method: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({
                    torrents
                }),
                success: () => {
                    showAlert(`✅ ${torrents.length} torrents sent for download.`, () => {
                        showConfirm('Do you want to go check downloads?', ok => {
                            if (ok) window.location.href = TORRENTS_URL;
                        });
                    });
                },
                error: () => {
                    showAlert('❌ Failed to send torrents for download.');
                }
            });
        });
    });
    
    // Initialize search input state
    if ($('#searchQuery').val().trim().length > 0) {
        $('#clearSearchBtn').show();
        // Auto-search if a query is provided in the URL
        doSearch();
    }
    
    $('#contentArea').on('click', 'li', function () {
        const link = $(this).data('link');
        selected.has(link) ? selected.delete(link) : selected.add(link);
        updateBulkBtn();
        $(this).toggleClass('bg-info text-dark');
    });
    
    $('#bulkDownloadBtn').click(() => {
        if (!selected.size) return;
        const torrents = Array.from(selected).map(l => ({
            link: l
        }));
        $.ajax({
            url: '/search/download/',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                torrents
            }),
            success: () => {
                // First show alert, then after it's closed ask confirm
                showAlert(`✅ ${selected.size} selected torrents sent for download.`, () => {
                    selected.clear();
                    updateBulkBtn();
                    fullRender();
                    showConfirm('Do you want to go check downloads?', ok => {
                        if (ok) window.location.href = TORRENTS_URL;
                    });
                });
            },
            error: () => {
                showAlert('❌ Failed to send torrents for download.');
            }
        });
    });

    fullRender();
});
