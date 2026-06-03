# Trading Journal

A local, private trading journal built with Python, Streamlit, and SQLite. Designed to connect macro market events to trade ideas and build a structured record of learning over time.

## Features

### Dashboard
- Summary metrics: total events, trades, open positions, and closed P&L
- Recent market events and trades at a glance

### News & Market Events
- Log macro data, earnings, Fed speeches, geopolitical events, and more
- Fields: date, category, asset class, market reaction, interpretation, importance (1–5), tags
- Filter by category, asset class, and date range
- Edit and delete entries inline

### Trades & Trade Ideas
- Record live trades or paper trades with full pre- and post-trade detail
- Fields: asset, direction, time horizon, thesis, catalyst, entry/target/stop, confidence (1–5), risk factors, status, actual exit, P&L, post-trade review
- Link each trade to a related news event
- Filter by status, asset class, and direction
- Edit and delete entries inline

### Learning Notes
- Personal knowledge base for macro, sectors, options/volatility, risk management, trading psychology, Python/data, and more
- Rich content field with category, subcategory, and tags
- Attach images via file upload or paste directly from clipboard
- Link notes to related market events or trades
- Filter by category, subcategory, and tag

## Tech Stack

- [Streamlit](https://streamlit.io) — UI framework
- SQLite — local database (no server required)
- [streamlit-paste-button](https://github.com/giorgiop/streamlit-paste-button) — clipboard image paste

## Setup

**1. Clone the repo**
```bash
git clone https://github.com/ethanzhu819/trading-journal.git
cd trading-journal
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Run the app**
```bash
streamlit run app.py
```

The app opens in your browser at `http://localhost:8501`. The SQLite database (`trading_journal.db`) and uploaded images (`uploads/`) are created automatically on first run and are excluded from version control.

## Project Structure

```
trading-journal/
├── app.py              # Dashboard and entry point
├── database.py         # SQLite schema and all CRUD functions
├── pages/
│   ├── news.py         # News & Market Events page
│   ├── trades.py       # Trades & Trade Ideas page
│   └── learning.py     # Learning Notes page
└── requirements.txt
```

## Notes

- All data is stored locally. Nothing is sent to external services.
- The database file and uploaded images are gitignored and never pushed to GitHub.
- For personal use only. Do not connect to brokerage accounts or live trading systems.
