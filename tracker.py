from playwright.sync_api import sync_playwright
import re

URL = "https://www.profinfo.pl/sklep/komentarz-do-spraw-o-podzial-majatku-wspolnego-malzonkow,157665.html"

print("➡️ Start Playwright...")

def parse_price(text):
    # wyciąga liczbę z "197,03 zł"
    return float(text.replace("zł", "").replace(",", ".").strip())

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    print("➡️ Otwieram stronę...")
    page.goto(URL, timeout=60000)

    # czekamy aż załaduje się sekcja z produktami
    page.wait_for_selector(".rwd-option-product", timeout=15000)

    print("➡️ Szukam cen...")

    options = page.locator(".rwd-option-product")
    count = options.count()

    print(f"Znaleziono opcji: {count}")

    results = {}

    for i in range(count):
        option = options.nth(i)

        # sprawdzamy typ produktu
        input_el = option.locator("input")
        data_type = input_el.get_attribute("data-type")

        if data_type in ["book", "book_paper_ebooks"]:
            print(f"\n➡️ Analizuję: {data_type}")

            # najpierw próbujemy promo
            promo = option.locator(".price-promo")

            if promo.count() > 0:
                price_text = promo.inner_text()
                print(f"💰 Promo price: {price_text}")
            else:
                # fallback jeśli nie ma promo
                price_text = option.locator(".price").inner_text()
                print(f"💰 Regular price: {price_text}")

            price = parse_price(price_text)

            results[data_type] = price

    browser.close()

print("\n📊 WYNIKI:")
for k, v in results.items():
    print(f"{k}: {v} zł")
