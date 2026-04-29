import logging
import requests
import json
import os
import time
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv
from pages.page_factory import get_page_for_url

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

PRODUCTS_FILE = "products.json"

with open(PRODUCTS_FILE, "r") as f:
    PRODUCTS = json.load(f)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
PRICE_HISTORY_FILE = "last_price.json"

def get_prices(url, retries=3):
    for attempt in range(retries):
        try:
            with sync_playwright() as p:
                headless = os.getenv("GITHUB_ACTIONS") == "true"
                browser = p.chromium.launch(headless=headless)
                product_page = get_page_for_url(url, browser.new_page())
                product_page.open(url)
                current_price = product_page.get_current_price()
                original_price = product_page.get_original_price(current_price)
                browser.close()
                return current_price, original_price

        except Exception as e:
            logger.warning(f"Attempt {attempt + 1} of {retries} failed: {e}")
            if attempt + 1 == retries:
                raise
            logger.info("Retrying in 5 seconds...")
            time.sleep(5)

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    response = requests.post(url, json=payload)
    logger.debug(f"Telegram response: {response.json()}")

def load_price_history():
    if os.path.exists(PRICE_HISTORY_FILE):
        with open(PRICE_HISTORY_FILE, "r") as f:
            return json.load(f)
    return {}

def save_price_history(history):
    with open(PRICE_HISTORY_FILE, "w") as f:
        json.dump(history, f)

def check_deal(product, current_price, original_price, history):
    logger.info(f"--- {product['name']} ---")
    logger.info(f"Current price: {current_price} Lei")

    last_price = history.get(product["name"])
    logger.info(f"Last known price: {last_price} Lei")

    if current_price != last_price:
        logger.info("Price changed! Saving new price...")
        history[product["name"]] = current_price

        discount_text = ""
        if original_price is not None and original_price > current_price:
            discount = ((original_price - current_price) / original_price) * 100
            discount_text = f"\nDiscount: {discount:.1f}%\nOriginal price: {original_price} Lei"

        message = (
            f"💰 Price change detected on eMAG!\n"
            f"Product: {product['name']}\n"
            f"Old price: {last_price} Lei\n"
            f"New price: {current_price} Lei"
            f"{discount_text}\n"
            f"Link: {product['url']}"
        )
        logger.info(message)
        send_telegram_message(message)
    else:
        logger.info("Price unchanged. No notification sent.")

if __name__ == "__main__":
    history = load_price_history()
    for product in PRODUCTS:
        try:
            current, original = get_prices(product["url"])
            check_deal(product, current, original, history)
        except Exception as e:
            logger.error(f"Error tracking {product['name']}: {e}")
    save_price_history(history)
