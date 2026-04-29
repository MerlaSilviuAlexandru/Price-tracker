from unittest.mock import patch
from tracker import check_deal

PRODUCT = {
    "name": "Test Product",
    "url": "https://www.emag.ro/test-product"
}
SITE_NAME = "eMAG"


@patch("tracker.send_telegram_message")
def test_price_drop_sends_notification(mock_send):
    history = {"Test Product": 100.0}
    check_deal(PRODUCT, 80.0, None, SITE_NAME, history, {})
    mock_send.assert_called_once()


@patch("tracker.send_telegram_message")
def test_price_increase_no_notification(mock_send):
    history = {"Test Product": 100.0}
    check_deal(PRODUCT, 120.0, None, SITE_NAME, history, {})
    mock_send.assert_not_called()


@patch("tracker.send_telegram_message")
def test_price_increase_updates_history(mock_send):
    history = {"Test Product": 100.0}
    check_deal(PRODUCT, 120.0, None, SITE_NAME, history, {})
    assert history["Test Product"] == 120.0


@patch("tracker.send_telegram_message")
def test_price_unchanged_no_notification(mock_send):
    history = {"Test Product": 100.0}
    check_deal(PRODUCT, 100.0, None, SITE_NAME, history, {})
    mock_send.assert_not_called()


@patch("tracker.send_telegram_message")
def test_price_drop_updates_history(mock_send):
    history = {"Test Product": 100.0}
    check_deal(PRODUCT, 80.0, None, SITE_NAME, history, {})
    assert history["Test Product"] == 80.0


@patch("tracker.send_telegram_message")
def test_price_drop_with_discount_includes_discount_text(mock_send):
    history = {"Test Product": 100.0}
    check_deal(PRODUCT, 80.0, 120.0, SITE_NAME, history, {})
    message = mock_send.call_args[0][0]
    assert "Discount:" in message
    assert "Original price:" in message


@patch("tracker.send_telegram_message")
def test_price_drop_without_discount_no_discount_text(mock_send):
    history = {"Test Product": 100.0}
    check_deal(PRODUCT, 80.0, None, SITE_NAME, history, {})
    message = mock_send.call_args[0][0]
    assert "Discount:" not in message


@patch("tracker.send_telegram_message")
def test_first_time_product_no_notification(mock_send):
    history = {}
    check_deal(PRODUCT, 100.0, None, SITE_NAME, history, {})
    mock_send.assert_not_called()


@patch("tracker.send_telegram_message")
def test_first_time_product_saves_baseline(mock_send):
    history = {}
    check_deal(PRODUCT, 100.0, None, SITE_NAME, history, {})
    assert history["Test Product"] == 100.0


@patch("tracker.send_telegram_message")
def test_notification_message_contains_product_name(mock_send):
    history = {"Test Product": 100.0}
    check_deal(PRODUCT, 80.0, None, SITE_NAME, history, {})
    message = mock_send.call_args[0][0]
    assert "Test Product" in message


@patch("tracker.send_telegram_message")
def test_notification_message_contains_old_and_new_price(mock_send):
    history = {"Test Product": 100.0}
    check_deal(PRODUCT, 80.0, None, SITE_NAME, history, {})
    message = mock_send.call_args[0][0]
    assert "100.0" in message
    assert "80.0" in message


@patch("tracker.send_telegram_message")
def test_dry_run_skips_notification(mock_send):
    history = {"Test Product": 100.0}
    check_deal(PRODUCT, 80.0, None, SITE_NAME, history, {}, dry_run=True)
    mock_send.assert_not_called()


@patch("tracker.send_telegram_message")
def test_dry_run_does_not_update_history(mock_send):
    history = {"Test Product": 100.0}
    check_deal(PRODUCT, 80.0, None, SITE_NAME, history, {}, dry_run=True)
    assert history["Test Product"] == 100.0


@patch("tracker.send_telegram_message")
def test_notification_contains_site_name(mock_send):
    history = {"Test Product": 100.0}
    check_deal(PRODUCT, 80.0, None, "Altex", history, {})
    message = mock_send.call_args[0][0]
    assert "Altex" in message


@patch("tracker.send_telegram_message")
def test_all_time_low_text_shown_when_price_beats_record(mock_send):
    history = {"Test Product": 100.0}
    lowest = {"Test Product": 90.0}
    check_deal(PRODUCT, 80.0, None, SITE_NAME, history, lowest)
    message = mock_send.call_args[0][0]
    assert "All-time low" in message


@patch("tracker.send_telegram_message")
def test_all_time_low_text_shown_when_price_matches_record(mock_send):
    history = {"Test Product": 100.0}
    lowest = {"Test Product": 80.0}
    check_deal(PRODUCT, 80.0, None, SITE_NAME, history, lowest)
    message = mock_send.call_args[0][0]
    assert "All-time low" in message


@patch("tracker.send_telegram_message")
def test_all_time_low_text_not_shown_when_price_above_record(mock_send):
    history = {"Test Product": 100.0}
    lowest = {"Test Product": 70.0}
    check_deal(PRODUCT, 80.0, None, SITE_NAME, history, lowest)
    message = mock_send.call_args[0][0]
    assert "All-time low" not in message


@patch("tracker.send_telegram_message")
def test_all_time_low_updated_when_new_record_set(mock_send):
    history = {"Test Product": 100.0}
    lowest = {"Test Product": 90.0}
    check_deal(PRODUCT, 80.0, None, SITE_NAME, history, lowest)
    assert lowest["Test Product"] == 80.0


@patch("tracker.send_telegram_message")
def test_all_time_low_not_updated_when_price_matches_record(mock_send):
    history = {"Test Product": 100.0}
    lowest = {"Test Product": 80.0}
    check_deal(PRODUCT, 80.0, None, SITE_NAME, history, lowest)
    assert lowest["Test Product"] == 80.0
