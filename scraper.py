from bs4 import BeautifulSoup
import requests


def scrape_all_magnets(url):
    resp = requests.get(url)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'html.parser')
    icons = soup.find_all('i', class_='fa-magnet')
    magnets = []
    for icon in icons:
        a = icon.find_parent('a')
        if a and 'href' in a.attrs:
            magnets.append(a['href'])
    return magnets