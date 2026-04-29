from utils import parse_price


class AltexProductPage:
    def __init__(self, page):
        self.page = page

    def open(self, url):
        self.page.goto(url, timeout=60000)
        self.page.wait_for_timeout(3000)

    def get_current_price(self):
        # text-3xl targets the main product section, not the sticky header (text-28px)
        raw = self.page.locator("div[class*='text-3xl']").first.inner_text()
        return parse_price(raw)

    def get_original_price(self, current_price):
        strikethrough = self.page.locator("[class*='has-line-through']")
        if strikethrough.count() == 0:
            return None
        raw = strikethrough.first.inner_text()
        original = parse_price(raw)
        if original < current_price:
            return None
        return original
