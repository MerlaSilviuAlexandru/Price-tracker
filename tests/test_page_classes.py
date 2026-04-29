from pages.base_page import BasePage
from pages.emag_page import EmagProductPage
from pages.altex_page import AltexProductPage


def test_base_page_site_name_is_none():
    assert BasePage.site_name is None


def test_emag_page_site_name():
    assert EmagProductPage.site_name == "eMAG"


def test_altex_page_site_name():
    assert AltexProductPage.site_name == "Altex"


def test_emag_inherits_from_base_page():
    assert issubclass(EmagProductPage, BasePage)


def test_altex_inherits_from_base_page():
    assert issubclass(AltexProductPage, BasePage)
