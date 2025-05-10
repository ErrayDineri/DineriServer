import qbittorrentapi
import os
import subprocess
import sys
import psutil
import time
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Constants
QB_HOST = 'localhost:8090'
qbittorrent_path = os.getenv("qbittorrentPATH")
DOWNLOAD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'media', 'videos'))

# Global client
qb_client = None

def start_qbittorrent():
    if not qbittorrent_path:
        raise EnvironmentError("The 'qbittorrentPATH' variable is not set in the .env file.")

    for proc in psutil.process_iter(['name']):
        if proc.info['name'] and 'qbittorrent' in proc.info['name'].lower():
            return  # Already running

    print("Starting qBittorrent...")
    subprocess.Popen([qbittorrent_path, "--webui-port=8090"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(3)  # Wait for Web UI to start

def init_client():
    global qb_client
    start_qbittorrent()

    client = qbittorrentapi.Client(host=QB_HOST)
    try:
        client.auth_log_in()
    except qbittorrentapi.LoginFailed as e:
        raise RuntimeError(f"Login to qBittorrent failed: {e}")
    
    qb_client = client

def ensure_client():
    global qb_client
    if qb_client is None:
        init_client()
    try:
        qb_client.app_version()
    except qbittorrentapi.APIConnectionError:
        init_client()

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