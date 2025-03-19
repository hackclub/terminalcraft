import requests 
from fake_useragent import UserAgent
from bs4 import BeautifulSoup

MIRROR_SOURCES = ["GET", "Cloudflare", "IPFS.io", "Infura"]

mirror_1 = "/adsa05c87b5d050a96b013e82e238f6f578OFY00YOW"

page = requests.get(f"https://libgen.li/{mirror_1}")

soup = BeautifulSoup(page.text, "html.parser")
links = soup.find_all("a", string=MIRROR_SOURCES)

print(links)
print(links[0]["href"])
def resolve_download_links(self, item):
    if self.is_plus:
        ua = UserAgent()
        headers = {"User-Agent": str(ua.firefox)}
        page = requests.get(f"https://libgen.li/{mirror_1}", headers=headers)
    else:
        page = requests.get(mirror_1)
    soup = BeautifulSoup(page.text, "html.parser")
    links = soup.find_all("a", string=MIRROR_SOURCES)

    if self.is_plus:
        download_links = {link.string: f"https://libgen.li/{link['href']}" for link in links}
    else:
        download_links = {link.string: link["href"] for link in links}
    
    print(download_links)