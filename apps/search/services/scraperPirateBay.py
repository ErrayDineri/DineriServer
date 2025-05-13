import requests
from urllib.parse import quote, urlparse, parse_qs

API_SERVER      = "https://apibay.org"
PRECOMPILED_URL = f"{API_SERVER}/precompiled"
SEARCH_API      = f"{API_SERVER}/q.php"
DETAIL_API      = f"{API_SERVER}/t.php"

TRACKERS = [
    "udp://tracker.opentrackr.org:1337",
    "udp://open.stealth.si:80/announce",
    "udp://tracker.torrent.eu.org:451/announce",
    "udp://tracker.bittor.pw:1337/announce",
    "udp://public.popcorn-tracker.org:6969/announce",
    "udp://tracker.dler.org:6969/announce",
    "udp://exodus.desync.com:6969",
    "udp://open.demonii.com:1337/announce",
]

def fetch_search(query: str, cat: str = "0"):
    params = {"q": query}
    if cat and cat != "0":
        params["cat"] = cat
    r = requests.get(SEARCH_API, params=params)
    r.raise_for_status()
    return r.json()

def fetch_top100(kind: str):
    url = f"{PRECOMPILED_URL}/data_top100_{kind}.json"
    r = requests.get(url)
    r.raise_for_status()
    return r.json()

def fetch_detail(torrent_id: str):
    r = requests.get(DETAIL_API, params={"id": torrent_id})
    r.raise_for_status()
    return r.json()

def make_magnet(info_hash: str, name: str) -> str:
    m = f"magnet:?xt=urn:btih:{info_hash}&dn={quote(name)}"
    for tr in TRACKERS:
        m += f"&tr={quote(tr)}"
    return m

def parse_tpb_url(url: str):
    """Extract mode/data (search vs detail) from a TPB-style URL."""
    parsed = urlparse(url)
    qs = parse_qs(parsed.query)
    if "id" in qs:
        return "detail", qs["id"][0]
    q = qs.get("q", [""])[0]
    cat = qs.get("cat", ["0"])[0]
    return "search", (q, cat)

def scrapePirateBay(url:str):
    mode, data = parse_tpb_url(url)
    magnets = []
    if mode == "detail":
        d = fetch_detail(data)
        if d:
            magnets.append(make_magnet(d["info_hash"], d["name"]))
    else:
        q, cat = data
        if not q:
            return None
        if q.startswith("top100:"):
            kind = q.split(":",2)[1]
            items = fetch_top100(kind)
        else:
            items = fetch_search(q, cat)

        for t in items:
            magnets.append(make_magnet(t["info_hash"], t["name"]))
    return magnets