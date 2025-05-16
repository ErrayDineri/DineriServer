import qbittorrentapi
import os
import subprocess
import psutil
import time
import environ
import platform
import shutil
import requests  # Added for check_qbittorrent_webui function

env = environ.Env()
environ.Env.read_env()  # This reads the .env file

QB_HOST = 'localhost:8090'
def detect_qbittorrent_path():
    # First check if it's in PATH
    qbittorrent = shutil.which("qbittorrent")
    if qbittorrent:
        return qbittorrent

    # Windows common path
    if platform.system() == "Windows":
        possible_paths = [
            "C:/Program Files/qBittorrent/qbittorrent.exe",
            "C:/Program Files (x86)/qBittorrent/qbittorrent.exe",
        ]
    elif platform.system() == "Darwin":  # macOS
        possible_paths = [
            "/Applications/qbittorrent.app/Contents/MacOS/qbittorrent",
        ]
    else:  # Linux
        possible_paths = [
            "/usr/bin/qbittorrent-nox",
            "/usr/bin/qbittorrent",
            "/usr/local/bin/qbittorrent-nox",
            "/usr/local/bin/qbittorrent",
        ]

    for path in possible_paths:
        if os.path.isfile(path):
            return path

    return None
qbittorrent_path = detect_qbittorrent_path()

# Path to the media directory in the project root
DOWNLOAD_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'media', 'videos'))

# Global client
qb_client = None

def start_qbittorrent():
    if not qbittorrent_path:
        raise EnvironmentError("qBittorrent path not found. Please install qBittorrent.")

    # Check if qBittorrent is already running
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] and 'qbittorrent' in proc.info['name'].lower():
            print("qBittorrent is already running")
            return True  # Already running

    print(f"Starting qBittorrent from: {qbittorrent_path}...")
    try:
        subprocess.Popen([qbittorrent_path, "--webui-port=8090"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("qBittorrent process started, waiting for WebUI to initialize...")
        
        # Wait for qBittorrent to start up properly
        time.sleep(3)  
        
        # Verify it's running
        for proc in psutil.process_iter(['name']):
            if proc.info['name'] and 'qbittorrent' in proc.info['name'].lower():
                print("qBittorrent is now running")
                return True
                
        print("Failed to verify qBittorrent is running")
        return False
    except Exception as e:
        print(f"Error starting qBittorrent: {e}")
        return False

def init_client():
    global qb_client
    try:
        # Start qBittorrent if not already running
        qbittorrent_started = start_qbittorrent()
        if not qbittorrent_started:
            print("Failed to start qBittorrent, cannot proceed")
            return False
            
        # Try to connect with default credentials (no username/password)
        print(f"Connecting to qBittorrent WebUI at {QB_HOST}...")
        client = qbittorrentapi.Client(host=QB_HOST)
        
        # Try to log in (default is admin/adminadmin)
        try:
            client.auth_log_in(username="admin", password="adminadmin")
        except:
            # Try without credentials - some installations don't require them
            try:
                client.auth_log_in()
            except Exception as e:
                print(f"Authentication failed: {e}")
                print("Make sure WebUI is enabled in qBittorrent settings with correct credentials")
                return False
        
        print("Successfully connected and logged in to qBittorrent WebUI")
        qb_client = client
        return True
    except Exception as e:
        print(f"Error initializing qBittorrent client: {e}")
        return False

def ensure_client():
    global qb_client
    
    # If client doesn't exist, initialize it
    if qb_client is None:
        print("qBittorrent client not initialized, initializing...")
        success = init_client()
        if not success:
            raise RuntimeError("Failed to initialize qBittorrent client")
        return
    
    # Test if existing client is still connected
    try:
        version = qb_client.app_version()
        print(f"Connected to qBittorrent {version}")
    except Exception as e:
        print(f"Error connecting to qBittorrent: {e}, reinitializing...")
        success = init_client()
        if not success:
            raise RuntimeError("Failed to reinitialize qBittorrent client")
            
# Add a helper function to check WebUI status
def check_qbittorrent_webui():
    """Check if qBittorrent WebUI is running and accessible"""
    try:
        url = f"http://{QB_HOST}/api/v2/app/version"
        response = requests.get(url, timeout=2)
        if response.status_code == 200:
            return True
    except:
        pass
    return False

def downloadTorrent(link: str):
    ensure_client()
    qb_client.torrents_add(
        urls=link,
        is_first_last_piece_priority=True,
        is_sequential_download=True,
        save_path=DOWNLOAD_DIR
    )

def serialize_torrent(torrent):
    return {
        'name': torrent.name,
        'hash': torrent.hash,
        'state': torrent.state,
        'progress': round(torrent.progress * 100, 2),  # in %
        'download_speed': "{:.2f}".format(torrent.dlspeed / 1024),  # KB/s to MB/s, rounded to 2 decimal places
        'upload_speed': "{:.2f}".format(torrent.upspeed / 1024),  # KB/s to MB/s, rounded to 2 decimal places
        'eta': torrent.eta,  # seconds
        'size': round(torrent.size / (1024 * 1024), 2),  # MB
        'downloaded': round(torrent.downloaded / (1024 * 1024), 2),  # MB
        'uploaded': round(torrent.uploaded / (1024 * 1024), 2),  # MB
        'save_path': torrent.save_path,
        'is_completed': torrent.state.lower() == 'uploading' or torrent.progress == 1.0,
        'added_on': torrent.added_on,
        'num_seeds': torrent.num_seeds,
        'num_peers': torrent.num_leechs,
    }

def getAllTorrentsSerialized():
    ensure_client()
    torrents = qb_client.torrents_info()
    torrents = map(serialize_torrent, torrents)

    # Sorting torrents:
    torrents = sorted(torrents, key=lambda t: (
        t['state'] != 'downloading',  # 'downloading' torrents first (False < True)
        -t['progress'] if t['state'] == 'downloading' else float('inf')  # Sort by progress for downloading torrents
    ))

    # Ensure download_speed and upload_speed are displayed correctly with 2 decimal places
    for torrent in torrents:
        torrent['download_speed'] = "{:.2f}".format(float(torrent['download_speed']) / 1024)  # Convert KB/s to MB/s
        torrent['upload_speed'] = "{:.2f}".format(float(torrent['upload_speed']) / 1024)  # Convert KB/s to MB/s
    return torrents


def pauseTorrent(hash: str):
    ensure_client()
    qb_client.torrents_pause(torrent_hashes=hash)

def resumeTorrent(hash: str):
    ensure_client()
    qb_client.torrents_resume(torrent_hashes=hash)

def forceStartTorrent(hash: str):
    ensure_client()
    qb_client.torrents_forcestart(torrent_hashes=hash)

def deleteTorrent(hash: str, delete_files: bool=False):
    ensure_client()
    qb_client.torrents_delete(torrent_hashes=hash, delete_files=delete_files)