from playwright.sync_api import sync_playwright
import json
import os
from datetime import datetime

URL = "https://www.profinfo.pl/sklep/komentarz-do-spraw-o-podzial-majatku-wspolnego-malzonkow,157665.html"

FILE = "prices.json"


def parse_price(text):
    return float(text.replace("zł", "").replace(",", ".").strip())


def load_data():
    if not os.path.exists(FILE):
        return []
    with open(FILE, "r") as f:
        return json.load(f)


def save_data(data):
    with open(FILE, "w") as f:
        json.dump(data, f, indent=2)


def get_prices():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto(URL, timeout=60000)
        page.wait_for_selector(".rwd-option-product", timeout=15000)

        options = page.locator(".rwd-option-product")
        count = options.count()

        results = {}

        for i in range(count):
            option = options.nth(i)
            input_el = option.locator("input")
            data_type = input_el.get_attribute("data-type")

            if data_type in ["book", "book_paper_ebooks"]:
                promo = option.locator(".price-promo")

                if promo.count() > 0:
                    price_text = promo.inner_text()
                else:
                    price_text = option.locator(".price").inner_text()

                price = parse_price(price_text)
                results[data_type] = price

        browser.close()
        return results


def main():
    print("➡️ Start trackera...")

    current = get_prices()
    history = load_data()

    print(f"📊 Aktualne ceny: {current}")

    # ostatni wpis
    last = history[-1]["prices"] if history else {}

    # najniższe ceny w historii
    min_prices = {}

    for entry in history:
        for k, v in entry["prices"].items():
            if k not in min_prices or v < min_prices[k]:
                min_prices[k] = v

    # 🔔 logika alertów
    for k, price in current.items():
        print(f"\n➡️ {k}: {price} zł")

        if k in last and price < last[k]:
            print(f"🔻 SPADŁA (było {last[k]})")

        if k not in min_prices or price < min_prices[k]:
            print(f"🔥 NAJNIŻSZA EVER!")

    # zapis
    history.append({
        "date": datetime.now().isoformat(),
        "prices": current
    })

    save_data(history)


if __name__ == "__main__":
    main()
