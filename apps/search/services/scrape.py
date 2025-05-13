from bs4 import BeautifulSoup
import requests
import re
from .scraperPirateBay import scrapePirateBay
import cloudscraper

def get_size_only(td):
    return ''.join(td.find_all(string=True, recursive=False)).strip()

def souper(url:str):
    resp = requests.get(url)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'html.parser')
    return soup

def souperCloud(url:str):
    scraper = cloudscraper.create_scraper()
    resp = scraper.get(url)
    soup = BeautifulSoup(resp.text, 'html.parser')
    return soup

def scrapeNyaa(url:str):
    soup = souper(url)
    icons = soup.find_all('i', class_='fa-magnet')
    magnets = []
    for icon in icons:
        a = icon.find_parent('a')
        if a and 'href' in a.attrs:
            magnets.append(a['href'])
    return magnets

def scrape1337x(url: str):
    soup=souper(url)
    all_js = "\n".join(script.string or "" for script in soup.find_all('script'))
    m = re.search(r'''var\s+mainMagnetURL\s*=\s*"([^"]+)";''', all_js)
    return [m.group(1)] if m else None

def scrape_all_magnets(url:str):
    if 'nyaa.si' in url:
        return scrapeNyaa(url)
    elif '1337x.to' in url:
        return scrape1337x(url)
    elif 'thepiratebay.org' in url:
        return scrapePirateBay(url)
    else:
        return None

if __name__ == "__main__":
    pass