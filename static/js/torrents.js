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

function renderRow(t) {
    return `
        <li class="clusterize-row torrent-item" data-state="${mapState(t.state)}" id="torrent-${t.hash}">
            <div class="torrent-card p-3 mb-3" style="background: rgba(255,255,255,0.05); border-radius: 8px;">
                <h5 class="text-white">${t.name}</h5>
                <div class="mb-2 text-white">
                    Progress: <span class="progress-text">${t.progress}%</span>
                </div>
                <div class="progress mb-2" style="height: 18px;">
                    <div class="progress-bar bg-success" role="progressbar" style="width:${t.progress}%"
                        aria-valuenow="${t.progress}" aria-valuemin="0" aria-valuemax="100">
                        ${t.progress}%
                    </div>
                </div>
                <p class="mb-1 text-white">
                    <strong>State:</strong> <span class="state">${mapState(t.state)}</span>
                </p>
                <p class="mb-1 text-white">
                    <strong>ETA:</strong> <span class="eta">${t.eta > 0 ? t.eta + 's' : '∞'}</span>
                </p>
                <p class="mb-1 text-white">
                    <strong>DL Speed:</strong> <span class="dlspeed">${t.download_speed} MB/s</span>
                </p>
                <p class="mb-3 text-white">
                    <strong>UL Speed:</strong> <span class="upspeed">${t.upload_speed} MB/s</span>
                </p>
                <p class="mb-1 text-white">
                    <strong>Seeds:</strong> <span class="seeds">${t.num_seeds}</span>
                    &nbsp;|&nbsp;
                    <strong>Peers:</strong> <span class="peers">${t.num_peers}</span>
                </p>

                <!-- Buttons -->
                <div class="mt-2 d-flex flex-wrap gap-2">
                    <button class="btn btn-outline-warning btn-sm btn-action pause" data-hash="${t.hash}">⏸
                        Pause</button>
                    <button class="btn btn-outline-success btn-sm btn-action resume" data-hash="${t.hash}">▶
                        Resume</button>
                    <button class="btn btn-outline-info btn-sm btn-action force" data-hash="${t.hash}">⏩ Force
                        Start</button>
                    <button class="btn btn-danger btn-sm btn-action delete-files" data-hash="${t.hash}">🗑
                        Delete+Files</button>
                    <button class="btn btn-outline-danger btn-sm btn-action delete" data-hash="${t.hash}">🗑
                        Remove</button>
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
            card.find('.eta').text(upd.eta > 0 ? `${upd.eta}s` : '∞');
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
