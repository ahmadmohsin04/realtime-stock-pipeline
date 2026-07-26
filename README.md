# Real-Time Stock Data Pipeline & Dashboard

![Tests](https://github.com/ahmadmohsin04/realtime-stock-pipeline/actions/workflows/tests.yml/badge.svg)

A live-updating dashboard that ingests streaming stock price data through an automated pipeline, computes derived trading metrics, and visualizes trends in real time.

**Live demo:** https://stock-dashboard-qh6l.onrender.com
*(Free-tier hosting: the app spins down after 15 minutes of inactivity and takes 30-60 seconds to wake back up on first visit.)*

## What it does

- Polls live stock prices (AAPL, MSFT, GOOGL, TSLA) every 60 seconds via yfinance
- Validates every incoming record before storage (pydantic)
- Deduplicates at the database level so repeated polls during closed market hours never create duplicate rows
- Computes rolling metrics — 5 & 20-period moving averages, momentum, volatility — using pandas
- Displays everything on an auto-refreshing Streamlit dashboard with live charts

## Architecture

[yfinance API]
│
▼
[Ingestion: APScheduler polling loop] ──► pydantic validation
│
▼
[SQLite: price_records] (unique constraint on ticker+timestamp)
│
▼
[Processing: pandas rolling calculations]
│
▼
[SQLite: processed_metrics]
│
▼
[Streamlit dashboard] ──► auto-refreshing charts + summary cards

## Tech stack

- **Ingestion:** Python, yfinance, APScheduler
- **Validation:** pydantic
- **Processing:** pandas
- **Storage:** SQLite + SQLAlchemy
- **Dashboard:** Streamlit + Plotly
- **Testing:** pytest, GitHub Actions CI
- **Deployment:** Docker, Render

## Running locally

```bash
python -m venv venv
venv\Scripts\Activate.ps1        # Windows
pip install -r requirements.txt

# Initialize the database
python scripts/init_db.py

# Run the dashboard (includes ingestion + processing in-process)
streamlit run src/dashboard/app.py
```

Or with Docker:
```bash
docker compose up --build
```

## Running tests

```bash
python -m pytest tests/test_calculator.py tests/test_schemas.py -v
```

## Documented tradeoffs

- **SQLite over PostgreSQL:** zero setup, sufficient for this write volume (4 tickers/minute). SQLAlchemy is used as an abstraction layer, so switching to PostgreSQL later only requires changing the connection string.
- **yfinance version left unpinned (`>=1.5.1`):** Yahoo's backend changes frequently enough that an exact pin previously broke ingestion entirely (see commit history). Every other dependency is pinned exactly.
- **Single-container deployment on Render free tier:** ingestion and the dashboard run in one process so they can share the same local SQLite file, since Render's free tier has no shared disk between separate services. This means the background scheduler only runs while the service is receiving traffic — not truly continuous on the free tier.
- **Ephemeral storage:** the free-tier filesystem resets on redeploy/restart. A production deployment would use a managed database (e.g. Render's paid persistent disk, or PostgreSQL) instead.

