import requests
from bs4 import BeautifulSoup
import time

def can_crawl(base_url, path='/brookfield-wi/general-contractors'):
    robots_url = base_url + '/robots.txt'
    r = requests.get(robots_url, timeout=10)
    if r.status_code == 200 and 'Disallow' in r.text:
        for line in r.text.splitlines():
            if line.startswith('Disallow') and path.startswith(line.split(':')[1].strip()):
                return False
    return True

def scrape_brookfield_contractors():
    base_url = 'https://www.buildzoom.com'
    path = '/brookfield-wi/general-contractors'
    url = base_url + path

    if not can_crawl(base_url, path):
        print("🚫 Crawling disallowed by robots.txt")
        return []

    resp = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'html.parser')

    contractors = []
    for card in soup.select('.contractor-card'):  # Update selector if needed
        name = card.select_one('.contractor-name')
        name = name.get_text(strip=True) if name else None
        loc = card.select_one('.contractor-location')
        loc = loc.get_text(strip=True) if loc else None
        contractors.append({'name': name, 'location': loc})

    return contractors

if __name__ == '__main__':
    data = scrape_brookfield_contractors()
    for c in data:
        print(f"- {c['name']} | {c['location']}")
