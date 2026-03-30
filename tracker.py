from playwright.sync_api import sync_playwright
import json
import os
from datetime import datetime
import requests

URL = "https://www.profinfo.pl/sklep/komentarz-do-spraw-o-podzial-majatku-wspolnego-malzonkow,157665.html"
FILE = "prices.json"


# --- TELEGRAM ---
def notify(msg):
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        print("⚠️ Brak danych Telegram")
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"

    response = requests.post(url, data={
        "chat_id": chat_id,
        "text": msg
    })

    print(f"📨 Telegram status: {response.status_code}")


# --- HELPERS ---
def parse_price(text):
    return float(text.replace("zł", "").replace(",", ".").strip())


def load_data():
    if not os.path.exists(FILE):
        return []

    try:
        with open(FILE, "r") as f:
            return json.load(f)
    except:
        print("⚠️ Uszkodzony JSON — reset")
        return []


def save_data(data):
    with open(FILE, "w") as f:
        json.dump(data, f, indent=2)


# --- SCRAPER ---
def get_prices():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        print("➡️ Otwieram stronę...")
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


# --- MAIN ---
def main():
    print("➡️ Start trackera...")
    notify("✅ Tracker działa!")
    current = get_prices()
    history = load_data()

    print(f"📊 Aktualne ceny: {current}")

    last = history[-1]["prices"] if history else {}

    # min history
    min_prices = {}
    for entry in history:
        for k, v in entry["prices"].items():
            if k not in min_prices or v < min_prices[k]:
                min_prices[k] = v

    # --- LOGIKA ALERTÓW ---
    for k, price in current.items():
        print(f"\n➡️ {k}: {price} zł")

        # spadek ceny
        if k in last and price < last[k]:
            msg = f"📉 {k} TANIEJ!\nByło: {last[k]} zł\nJest: {price} zł"
            print(msg)
            notify(msg)

        # najniższa cena ever
        if k not in min_prices or price < min_prices[k]:
            msg = f"🔥 NAJNIŻSZA CENA EVER!\n{k}: {price} zł"
            print(msg)
            notify(msg)

    # zapis historii
    history.append({
        "date": datetime.now().isoformat(),
        "prices": current
    })

    save_data(history)


if __name__ == "__main__":
    main()
