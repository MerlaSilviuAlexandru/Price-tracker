import argparse
import csv
import logging
import requests
import json
import os
import time
from datetime import datetime
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
LOWEST_PRICE_FILE = "lowest_price.json"
PRICE_LOG_FILE = "price_history.csv"


def get_prices(url, browser, retries=3):
    for attempt in range(retries):
        try:
            page = browser.new_page()
            product_page = get_page_for_url(url, page)
            product_page.open(url)
            current_price = product_page.get_current_price()
            original_price = product_page.get_original_price(current_price)
            site_name = product_page.site_name
            page.close()
            return current_price, original_price, site_name

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


def load_lowest_prices():
    if os.path.exists(LOWEST_PRICE_FILE):
        with open(LOWEST_PRICE_FILE, "r") as f:
            return json.load(f)
    return {}


def save_lowest_prices(lowest):
    with open(LOWEST_PRICE_FILE, "w") as f:
        json.dump(lowest, f)


def log_price_change(product_name, site_name, old_price, new_price):
    file_exists = os.path.exists(PRICE_LOG_FILE)
    with open(PRICE_LOG_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["timestamp", "product", "site", "old_price", "new_price"])
        writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), product_name, site_name, old_price, new_price])


def check_deal(product, current_price, original_price, site_name, history, lowest, dry_run=False):
    name = product["name"]
    logger.info(f"--- {name} ---")
    logger.info(f"Current price: {current_price} Lei")

    last_price = history.get(name)
    lowest_price = lowest.get(name)
    logger.info(f"Last known price: {last_price} Lei")
    logger.info(f"All-time low: {lowest_price} Lei")

    if last_price is None:
        logger.info("First time seeing this product. Saving baseline price.")
        if not dry_run:
            history[name] = current_price
            lowest[name] = current_price
            log_price_change(name, site_name, None, current_price)
    elif current_price < last_price:
        discount_text = ""
        if original_price is not None and original_price > current_price:
            discount = ((original_price - current_price) / original_price) * 100
            discount_text = f"\nDiscount: {discount:.1f}%\nOriginal price: {original_price} Lei"

        all_time_low_text = ""
        if lowest_price is None or current_price <= lowest_price:
            all_time_low_text = "\n🏆 All-time low price!"

        message = (
            f"💰 Price drop detected on {site_name}!\n"
            f"Product: {name}\n"
            f"Old price: {last_price} Lei\n"
            f"New price: {current_price} Lei"
            f"{discount_text}"
            f"{all_time_low_text}\n"
            f"Link: {product['url']}"
        )
        logger.info(message)

        if dry_run:
            logger.info("[DRY RUN] Telegram notification skipped.")
        else:
            history[name] = current_price
            if lowest_price is None or current_price < lowest_price:
                lowest[name] = current_price
            log_price_change(name, site_name, last_price, current_price)
            send_telegram_message(message)
    elif current_price > last_price:
        logger.info(f"Price increased from {last_price} to {current_price} Lei. No notification sent.")
        if not dry_run:
            history[name] = current_price
            log_price_change(name, site_name, last_price, current_price)
    else:
        logger.info("Price unchanged. No notification sent.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Scrape prices without sending notifications or saving history")
    args = parser.parse_args()

    if args.dry_run:
        logger.info("[DRY RUN] Mode active — no notifications will be sent, history will not be updated.")

    history = load_price_history()
    lowest = load_lowest_prices()
    headless = os.getenv("GITHUB_ACTIONS") == "true"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        for product in PRODUCTS:
            try:
                current, original, site_name = get_prices(product["url"], browser)
                check_deal(product, current, original, site_name, history, lowest, dry_run=args.dry_run)
            except Exception as e:
                logger.error(f"Error tracking {product['name']}: {e}")
        browser.close()

    if not args.dry_run:
        save_price_history(history)
        save_lowest_prices(lowest)
