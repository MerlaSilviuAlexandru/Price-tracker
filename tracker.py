import re
import requests
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv
import os

load_dotenv()

PRODUCT_URL = "https://www.emag.ro/scutece-pampers-active-baby-xxl-box-marimea-5-11-16-kg-150-buc-8001090172594/pd/D7J5Q2BBM/"
DISCOUNT_THRESHOLD = 30
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def get_prices():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(PRODUCT_URL)
        page.wait_for_timeout(3000)

        current_price_raw = page.locator("[data-test='main-price']").inner_text()
        current_price = float(re.sub(r'[^\d,]', '', current_price_raw).replace(',', '.'))

        original_price_raw = page.locator("s").first.inner_text()
        original_price = float(re.sub(r'[^\d,]', '', original_price_raw).replace(',', '.'))

        browser.close()
        return current_price, original_price

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }
    response = requests.post(url, json=payload)
    print(f"Telegram response: {response.json()}")

def check_deal(current_price, original_price):
    discount = ((original_price - current_price) / original_price) * 100
    print(f"Original price: {original_price} Lei")
    print(f"Current price: {current_price} Lei")
    print(f"Discount: {discount:.1f}%")

    if discount >= DISCOUNT_THRESHOLD:
        message = (
            f"🔥 DEAL FOUND on eMAG!\n"
            f"Original price: {original_price} Lei\n"
            f"Current price: {current_price} Lei\n"
            f"Discount: {discount:.1f}%\n"
            f"Link: {PRODUCT_URL}"
        )
        print(message)
        send_telegram_message(message)
        return True
    else:
        print(f"No deal yet. Current discount is only {discount:.1f}%.")
        return False

if __name__ == "__main__":
    current, original = get_prices()
    check_deal(current, original)