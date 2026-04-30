from unittest.mock import MagicMock
from pages.emag_page import EmagProductPage
from pages.altex_page import AltexProductPage
from pages.carrefour_page import CarrefourProductPage


# --- eMAG ---

def test_emag_get_current_price():
    mock_page = MagicMock()
    mock_page.locator.return_value.first.count.return_value = 1
    mock_page.locator.return_value.first.inner_text.return_value = "279,98 Lei"
    assert EmagProductPage(mock_page).get_current_price() == 279.98


def test_emag_get_original_price_returns_none_when_no_strikethrough():
    mock_page = MagicMock()
    mock_page.locator.return_value.first.locator.return_value.count.return_value = 0
    assert EmagProductPage(mock_page).get_original_price(279.98) is None


def test_emag_get_original_price_returns_value_when_strikethrough_exists():
    mock_page = MagicMock()
    strikethrough = mock_page.locator.return_value.first.locator.return_value
    strikethrough.count.return_value = 1
    strikethrough.first.inner_text.return_value = "350,00 Lei"
    assert EmagProductPage(mock_page).get_original_price(279.98) == 350.0


def test_emag_get_original_price_returns_none_when_original_lower_than_current():
    mock_page = MagicMock()
    strikethrough = mock_page.locator.return_value.first.locator.return_value
    strikethrough.count.return_value = 1
    strikethrough.first.inner_text.return_value = "200,00 Lei"
    assert EmagProductPage(mock_page).get_original_price(279.98) is None


# --- Altex ---

def test_altex_get_current_price_no_sale():
    mock_page = MagicMock()
    price_block = mock_page.locator.return_value.first
    price_block.locator.return_value.count.return_value = 0
    price_block.inner_text.return_value = "189,99 Lei"
    assert AltexProductPage(mock_page).get_current_price() == 189.99


def test_altex_get_current_price_with_sale():
    mock_page = MagicMock()
    price_block = mock_page.locator.return_value.first
    sale = price_block.locator.return_value
    sale.count.return_value = 1
    sale.first.inner_text.return_value = "150,00 Lei"
    assert AltexProductPage(mock_page).get_current_price() == 150.0


def test_altex_get_original_price_returns_none_when_no_strikethrough():
    mock_page = MagicMock()
    mock_page.locator.return_value.count.return_value = 0
    assert AltexProductPage(mock_page).get_original_price(189.99) is None


def test_altex_get_original_price_returns_value_when_strikethrough_exists():
    mock_page = MagicMock()
    strikethrough = mock_page.locator.return_value
    strikethrough.count.return_value = 1
    strikethrough.first.inner_text.return_value = "250,00 Lei"
    assert AltexProductPage(mock_page).get_original_price(189.99) == 250.0


def test_altex_get_original_price_returns_none_when_original_lower_than_current():
    mock_page = MagicMock()
    strikethrough = mock_page.locator.return_value
    strikethrough.count.return_value = 1
    strikethrough.first.inner_text.return_value = "100,00 Lei"
    assert AltexProductPage(mock_page).get_original_price(189.99) is None


# --- Carrefour ---

def test_carrefour_get_current_price():
    mock_page = MagicMock()
    mock_page.locator.return_value.first.get_attribute.return_value = "229.90"
    assert CarrefourProductPage(mock_page).get_current_price() == 229.90


def test_carrefour_get_original_price_returns_none_when_no_old_price():
    mock_page = MagicMock()
    mock_page.locator.return_value.count.return_value = 0
    assert CarrefourProductPage(mock_page).get_original_price(229.90) is None


def test_carrefour_get_original_price_returns_value_when_old_price_exists():
    mock_page = MagicMock()
    old_price_el = mock_page.locator.return_value
    old_price_el.count.return_value = 1
    old_price_el.first.get_attribute.return_value = "234.15"
    assert CarrefourProductPage(mock_page).get_original_price(229.90) == 234.15


def test_carrefour_get_original_price_returns_none_when_original_lower_than_current():
    mock_page = MagicMock()
    old_price_el = mock_page.locator.return_value
    old_price_el.count.return_value = 1
    old_price_el.first.get_attribute.return_value = "200.00"
    assert CarrefourProductPage(mock_page).get_original_price(229.90) is None
