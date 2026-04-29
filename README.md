# PriceTracker

A Python automation tool that monitors product prices across multiple e-commerce sites and sends a Telegram notification whenever a price changes.

## How it works

1. Reads the product list from `products.json`
2. Opens each product page using Playwright (headless in CI)
3. Scrapes the current price and original (strikethrough) price
4. Compares against the last known price stored in `last_price.json`
5. Sends a Telegram message if the price has changed
6. Saves the updated price history back to `last_price.json`

Runs automatically every hour via GitHub Actions.

## Project structure

```
emag-price-tracker/
├── pages/
│   └── emag_page.py   # Page Object — all Playwright/selector logic
├── tests/
│   ├── test_check_deal.py
│   ├── test_parse_price.py
│   ├── test_price_history.py
│   └── test_telegram.py
├── tracker.py          # Orchestration and business logic
├── utils.py            # Price parsing helper
├── products.json       # List of products to track
└── last_price.json     # Persisted price history
```

## Setup

### 1. Install dependencies

```bash
pip install playwright python-dotenv requests pytest
playwright install chromium
```

### 2. Create a `.env` file

```
TELEGRAM_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
```

### 3. Add products to track

Edit `products.json` — no code changes needed:

```json
[
    {
        "name": "Product Name",
        "url": "https://www.emag.ro/..."
    }
]
```

### 4. Run the tracker

```bash
python tracker.py
```

### 5. Run the tests

```bash
pytest tests/ -v
```

## CI/CD

GitHub Actions runs on every push and on an hourly schedule:

1. **test job** — runs the full pytest suite
2. **track-price job** — only runs if tests pass; scrapes prices and commits updated `last_price.json`

Secrets `TELEGRAM_TOKEN` and `TELEGRAM_CHAT_ID` must be configured in the repository settings under *Settings → Secrets and variables → Actions*.

## Tech stack

- Python 3.11
- Playwright (browser automation)
- Requests (Telegram API)
- python-dotenv
- pytest
- GitHub Actions
