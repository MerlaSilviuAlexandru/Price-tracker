import re
import requests
import json
import os
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

load_dotenv()

PRODUCTS = [
    {
        "name": "Pampers Active Baby Pants Size 5 164buc",
        "url": "https://www.emag.ro/scutece-chilotel-pampers-active-baby-pants-xxl-box-marimea-5-11kg-17kg-164-buc-8006530315722/pd/DGPTK32BM/"
    }
]

DISCOUNT_THRESHOLD = 30
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
PRICE_HISTORY_FILE = "last_price.json"

def get_prices(url):
    with sync_playwright() as p:
        headless = os.getenv("GITHUB_ACTIONS") == "true"
        browser = p.chromium.launch(headless=headless)
        page = browser.new_page()
        page.goto(url)
        page.wait_for_timeout(3000)

        current_price_raw = page.locator("[data-test='main-price']").first.inner_text()
        current_price = float(re.sub(r'[^\d,]', '', current_price_raw).replace(',', '.'))

        original_price = None
        pricing_block = page.locator(".product-highlight-price, .pricing-block").first
        strikethrough = pricing_block.locator("s")
        if strikethrough.count() > 0:
            original_price_raw = strikethrough.first.inner_text()
            original_price = float(re.sub(r'[^\d,]', '', original_price_raw).replace(',', '.'))
            if original_price < current_price:
                original_price = None

        browser.close()
        return current_price, original_price

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    response = requests.post(url, json=payload)
    print(f"Telegram response: {response.json()}")

def load_price_history():
    if os.path.exists(PRICE_HISTORY_FILE):
        with open(PRICE_HISTORY_FILE, "r") as f:
            return json.load(f)
    return {}

def save_price_history(history):
    with open(PRICE_HISTORY_FILE, "w") as f:
        json.dump(history, f)

def check_deal(product, current_price, original_price, history):
    print(f"\n--- {product['name']} ---")
    print(f"Current price: {current_price} Lei")

    if original_price is None:
        print("No discount available on this product right now.")
        history[product["name"]] = current_price
        return

    discount = ((original_price - current_price) / original_price) * 100
    last_price = history.get(product["name"])

    print(f"Original price: {original_price} Lei")
    print(f"Discount: {discount:.1f}%")
    print(f"Last known price: {last_price} Lei")

    if current_price != last_price:
        print("Price changed! Saving new price...")
        history[product["name"]] = current_price
        if discount >= DISCOUNT_THRESHOLD:
            message = (
                f"🔥 DEAL FOUND on eMAG!\n"
                f"Product: {product['name']}\n"
                f"Original price: {original_price} Lei\n"
                f"Current price: {current_price} Lei\n"
                f"Discount: {discount:.1f}%\n"
                f"Link: {product['url']}"
            )
            print(message)
            send_telegram_message(message)
        else:
            print(f"Price changed but discount is only {discount:.1f}%. No notification sent.")
    else:
        print("Price unchanged. No notification sent.")

if __name__ == "__main__":
    history = load_price_history()
    for product in PRODUCTS:
        try:
            current, original = get_prices(product["url"])
            check_deal(product, current, original, history)
        except Exception as e:
            print(f"Error tracking {product['name']}: {e}")
    save_price_history(history)