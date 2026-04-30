import os
import re
import requests
from pages.base_page import BasePage

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}

_PROXIES = (
    {"http": "socks5://127.0.0.1:9050", "https": "socks5://127.0.0.1:9050"}
    if os.getenv("CI")
    else {}
)


class EmagProductPage(BasePage):
    site_name = "eMAG"

    def __init__(self, page):
        super().__init__(page)
        self._html = None

    def open(self, url):
        response = requests.get(url, headers=_HEADERS, proxies=_PROXIES, timeout=30)
        response.raise_for_status()
        self._html = response.text

    def get_current_price(self):
        match = re.search(
            r'data-test="main-price">(\d+)<sup><small[^>]*>[^<]*</small>(\d+)</sup>',
            self._html,
        )
        if not match:
            raise ValueError("Price element not found in eMAG response")
        return float(f"{match.group(1)}.{match.group(2)}")

    def get_original_price(self, current_price):
        match = re.search(
            r'<s>(\d+)<sup><small[^>]*>[^<]*</small>(\d+)</sup>',
            self._html,
        )
        if not match:
            return None
        original = float(f"{match.group(1)}.{match.group(2)}")
        if original < current_price:
            return None
        return original

    def screenshot_on_failure(self, url):
        return None
