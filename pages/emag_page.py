from utils import parse_price
from pages.base_page import BasePage


class EmagProductPage(BasePage):
    site_name = "eMAG"

    def get_current_price(self):
        raw = self.page.locator("[data-test='main-price']").first.inner_text()
        return parse_price(raw)

    def get_original_price(self, current_price):
        pricing_block = self.page.locator(".product-highlight-price, .pricing-block").first
        strikethrough = pricing_block.locator("s")
        if strikethrough.count() == 0:
            return None
        raw = strikethrough.first.inner_text()
        original = parse_price(raw)
        if original < current_price:
            return None
        return original
