from pages.emag_page import EmagProductPage
from pages.altex_page import AltexProductPage


def get_page_for_url(url, playwright_page):
    if "emag.ro" in url:
        return EmagProductPage(playwright_page)
    if "altex.ro" in url:
        return AltexProductPage(playwright_page)
    raise ValueError(f"No page object configured for URL: {url}")
