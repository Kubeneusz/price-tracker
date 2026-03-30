import requests
from bs4 import BeautifulSoup

URL = "https://www.profinfo.pl/sklep/komentarz-do-spraw-o-podzial-majatku-wspolnego-malzonkow,157665.html"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

print("➡️ Start scrapowania...")

response = requests.get(URL, headers=HEADERS)

print(f"Status HTTP: {response.status_code}")

soup = BeautifulSoup(response.text, "html.parser")

# 🔍 próbujemy znaleźć cenę
price_tag = soup.select_one('[itemprop="price"]')

if price_tag:
    price = price_tag.get("content")
    print(f"💰 Znaleziona cena: {price} zł")
else:
    print("❌ Nie znaleziono ceny!")
    
    # DEBUG: pokaż kawałek HTML
    print("\n🔎 Fragment HTML:")
    print(soup.prettify()[:1000])
