class BasePage:
    site_name = None

    def __init__(self, page):
        self.page = page

    def open(self, url):
        self.page.goto(url, timeout=60000)
        self.page.wait_for_timeout(3000)
