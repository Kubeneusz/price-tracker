from playwright.sync_api import sync_playwright

URL = "https://www.profinfo.pl/sklep/komentarz-do-spraw-o-podzial-majatku-wspolnego-malzonkow,157665.html"

print("➡️ Start Playwright...")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    print("➡️ Otwieram stronę...")
    page.goto(URL, timeout=60000)

    print("➡️ Czekam na załadowanie ceny...")

    # 🔴 kluczowe — czekamy aż cena się pojawi
    page.wait_for_selector('[itemprop="price"]', timeout=15000)

    price = page.locator('[itemprop="price"]').get_attribute("content")

    print(f"💰 Cena: {price} zł")

    browser.close()
