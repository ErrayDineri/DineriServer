import requests
from bs4 import BeautifulSoup
from .scraperPirateBay import make_magnet
from .scrape import scrape1337x, souper, souperCloud, get_size_only

def searchNyaa(searchTerm):
    base_url = f"https://nyaa.si/?f=0&c=0_0&q={searchTerm}"
    soup=souper(base_url)
    elements=soup.find_all('tr')[1:]
    results=[]
    for element in elements:
        columns=element.find_all('td')
        results.append({
            'title': columns[1].find_all('a')[-1].text.strip(),
            'link': columns[2].find('i', class_='fa-magnet').find_parent('a')['href'],
            'size': columns[3].get_text(strip=True),
            'seeders': columns[5].get_text(strip=True),
            'leechers': columns[6].get_text(strip=True),
            'source' : 'Nyaa',
        })

    return results

def searchTPB(searchTerm):
    url = f"https://apibay.org/q.php?q={searchTerm}"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()

    results = []
    for item in data:
        if item.get("name"):  # ensure valid item
            results.append({
                "title": item["name"],
                "link": make_magnet(item["info_hash"], item["name"]),
                "size": f"{int(item['size']) / (1024 ** 3):.2f} GB",  # convert bytes to GB
                "seeders": item["seeders"],
                "leechers": item["leechers"],
                "source": "The Pirate Bay",
            })

    return results

def search1337x(searchTerm):
    url = f"https://1337x.to/search/{searchTerm}/1/"
    soup=souperCloud(url)
    elements=soup.find_all('tr')[1:]
    results=[]
    for element in elements[:6]:
        columns=element.find_all('td')
        
        results.append(
            {
                'title': columns[0].get_text(strip=True),
                'link': scrape1337x(f"https://1337x.to{columns[0].find_all('a')[-1]['href']}").pop(),
                'seeders': columns[1].get_text(strip=True),
                'leechers': columns[2].get_text(strip=True),
                'source': '1337x',
                'size': get_size_only(columns[4]),
            }
        )
    return results

def searchAll(searchTerm):
    results = []
    results.extend(searchNyaa(searchTerm))
    results.extend(searchTPB(searchTerm))
    results.extend(search1337x(searchTerm))
    return results

availableSources = ['Nyaa', 'The Pirate Bay', '1337x']
mapper={
    'Nyaa': searchNyaa,
    'The Pirate Bay': searchTPB,
    '1337x': search1337x
}
def searchBySource(searchTerm, source):
    if isinstance(source, list):
        res = []
        for s in source:
            if s in availableSources:
                res.extend(mapper[s](searchTerm))
        return res
    elif source in availableSources:
        return mapper[source](searchTerm=searchTerm)
    else:
        raise ValueError("Invalid source specified.")
if __name__ == "__main__":
    pass