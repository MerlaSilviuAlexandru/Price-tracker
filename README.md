# eMAG Price Tracker

A Python automation tool that monitors product prices on eMAG.ro and sends a Telegram notification when a deal is found.

## How it works
- Opens the product page using Playwright
- Extracts the current price and original price
- Calculates the discount percentage
- Sends a Telegram message if discount is above 30%

## Tech Stack
- Python
- Playwright
- Requests
- python-dotenv
- Telegram Bot API

## Setup

### 1. Install dependencies
```powershell
python -m pip install playwright python-dotenv requests
python -m playwright install
```

### 2. Create a `.env` file