// Torrent management functionality
let allTorrents = [],
    filteredTorrents = [],
    page = 1,
    previousProgress = {};
let currentFilter = 'all';

function mapState(s) {
    if (s === 'uploading' || s === 'stalledUP') return 'finished';
    if (s === 'forcedDL' || s === 'downloading') return 'downloading';
    if (s === 'queuedDL') return 'queuedDL';
    return s;
}

/**
 * Formats seconds into a human-readable time format (Xh Ym Zs)
 * Only shows units that are non-zero (e.g., won't show hours if 0)
 * @param {number} seconds - Total seconds
 * @return {string} Formatted time string
 */
function formatETA(seconds) {
    if (!seconds || seconds < 0) return '∞';
    if (seconds === 0) return 'Complete';
    
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);
    
    let result = '';
    
    if (hours > 0) {
        result += `${hours}h `;
    }
    
    if (minutes > 0 || hours > 0) {
        result += `${minutes}m `;
    }
    
    result += `${secs}s`;
    
    return result.trim();
}

function renderRow(t) {
    return `
        <li class="clusterize-row torrent-item stagger-item" data-state="${mapState(t.state)}" id="torrent-${t.hash}">
            <div class="torrent-card dark-mode-transition">
                <h5>${t.name}</h5>
                <div class="progress">
                    <div class="progress-bar bg-success" role="progressbar" style="width:${t.progress}%"
                        aria-valuenow="${t.progress}" aria-valuemin="0" aria-valuemax="100">
                        ${t.progress}%
                    </div>
                </div>
                
                <div class="torrent-info-group">
                    <div class="torrent-info-item">
                        <div class="label">State</div>
                        <div class="value state">${mapState(t.state)}</div>
                    </div>
                    <div class="torrent-info-item">
                        <div class="label">ETA</div>
                        <div class="value eta">${formatETA(t.eta)}</div>
                    </div>
                    <div class="torrent-info-item">
                        <div class="label">Download</div>
                        <div class="value dlspeed">${t.download_speed} MB/s</div>
                    </div>
                    <div class="torrent-info-item">
                        <div class="label">Upload</div>
                        <div class="value upspeed">${t.upload_speed} MB/s</div>
                    </div>
                    <div class="torrent-info-item">
                        <div class="label">Seeds / Peers</div>
                        <div class="value"><span class="seeds">${t.num_seeds}</span> / <span class="peers">${t.num_peers}</span></div>
                    </div>
                </div>

                <!-- Buttons -->
                <div class="mt-2 d-flex flex-wrap">
                    <button class="btn btn-outline-warning btn-sm btn-action pause" data-hash="${t.hash}">
                        <i class="fas fa-pause"></i> Pause
                    </button>
                    <button class="btn btn-outline-success btn-sm btn-action resume" data-hash="${t.hash}">
                        <i class="fas fa-play"></i> Resume
                    </button>
                    <button class="btn btn-outline-info btn-sm btn-action force" data-hash="${t.hash}">
                        <i class="fas fa-bolt"></i> Force Start
                    </button>
                    <button class="btn btn-danger btn-sm btn-action delete-files" data-hash="${t.hash}">
                        <i class="fas fa-trash-alt"></i> Delete+Files
                    </button>
                    <button class="btn btn-outline-danger btn-sm btn-action delete" data-hash="${t.hash}">
                        <i class="fas fa-times"></i> Remove
                    </button>
                </div>
            </div>
        </li>`;
}

let clusterize;

function initializeClusterize() {
    clusterize = new Clusterize({
        scrollElem: document.getElementById('scrollArea'),
        contentElem: document.getElementById('contentArea'),
        rows: []
    });
}

function loadTorrents(pg) {
    $.getJSON(TORRENT_STATUS_JSON_URL + "?page=" + pg, data => {
        allTorrents.push(...data.torrents);
        applyFilter(currentFilter);
    });
}

function applyFilter(state) {
    currentFilter = state;
    filteredTorrents = allTorrents.filter(t => {
        const ms = mapState(t.state);
        return state === 'all' || ms === state;
    });

    if (filteredTorrents.length === 0) {
        clusterize.update([
            `<li class="text-center text-white">🕵️‍♂️ No torrents match this filter.</li>`
        ]);
    } else {
        clusterize.update(filteredTorrents.map(renderRow));
    }
}

function updateTorrents() {
    $.getJSON(TORRENT_STATUS_JSON_URL + "?page=1", data => {
        data.torrents.forEach(nt => {
            const idx = allTorrents.findIndex(x => x.hash === nt.hash);
            if (idx > -1) allTorrents[idx] = nt;
        });

        filteredTorrents.forEach(t => {
            const card = $(`#torrent-${t.hash}`);
            if (!card.length) return;
            const upd = allTorrents.find(x => x.hash === t.hash);
            const pb = card.find('.progress-bar');
            const prev = previousProgress[t.hash] || 0;
            if (upd.progress > prev) {
                pb.addClass('bg-info');
                setTimeout(() => pb.removeClass('bg-info'), 500);
            }
            previousProgress[t.hash] = upd.progress;
            pb.css('width', `${upd.progress}%`).text(`${upd.progress}%`);
            card.find('.progress-text').text(`${upd.progress}%`);
            card.find('.state').text(mapState(upd.state));
            card.find('.eta').text(formatETA(upd.eta));
            card.find('.dlspeed').text(`${upd.download_speed} MB/s`);
            card.find('.upspeed').text(`${upd.upload_speed} MB/s`);
        });
    });
}

function getCSRF() {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
    if (csrfToken) {
        return csrfToken.value;
    }
    
    // Fallback to cookie parsing
    const cookieValue = document.cookie
        .split('; ')
        .find(row => row.startsWith('csrftoken='));
        
    if (cookieValue) {
        return cookieValue.split('=')[1];
    }
    
    console.error('CSRF token not found!');
    return '';
}

function torrentAction(action, hash, deleteFiles = false) {
    const urlMap = {
        pause: TORRENT_PAUSE_URL,
        resume: TORRENT_RESUME_URL,
        force: TORRENT_FORCE_URL,
        delete: TORRENT_DELETE_URL
    };

    let data = new FormData();
    data.append('hash', hash);
    if (action === 'delete' && deleteFiles) {
        data.append('delete_files', 'true');
    }

    console.log(`Sending ${action} action for hash: ${hash}`);
    
    $.ajax({
        type: 'POST',
        url: urlMap[action],
        data: data,
        processData: false,
        contentType: false,
        headers: {
            'X-CSRFToken': getCSRF()
        },
        success: resp => {
            console.log(`Action ${action} success:`, resp);
            if (resp.refresh) {
                // only reload on delete
                window.location.reload();
            } else {
                // for pause/resume/force, just update Progress & State
                updateTorrents();
            }
        },
        error: (xhr, status, error) => {
            console.error(`Action ${action} failed:`, {xhr, status, error});
            alert(`Failed to ${action} torrent: ${error}`);
        }
    });
}

$(function () {
    initializeClusterize();
    loadTorrents(page);
    setInterval(updateTorrents, 2000);

    // Handle infinite scroll
    $('#scrollArea').on('scroll', function () {
        const {
            scrollTop,
            scrollHeight,
            clientHeight
        } = this;
        if (scrollTop + clientHeight >= scrollHeight - 50) {
            page++;
            loadTorrents(page);
        }
    });
    
    // Button delegation
    $(document).on('click', '.btn-action', function () {
        const hash = $(this).data('hash');
        if (!hash) {
            console.error('No hash found on button:', this);
            return;
        }
        
        console.log('Button clicked:', this.className, 'Hash:', hash);
        
        if ($(this).hasClass('pause')) torrentAction('pause', hash);
        else if ($(this).hasClass('resume')) torrentAction('resume', hash);
        else if ($(this).hasClass('force')) torrentAction('force', hash);
        else if ($(this).hasClass('delete-files')) torrentAction('delete', hash, true);
        else if ($(this).hasClass('delete')) torrentAction('delete', hash, false);
    });
});
