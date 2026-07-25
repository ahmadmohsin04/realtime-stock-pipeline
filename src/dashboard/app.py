import sys
import os
sys.path.append(".")

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from dotenv import load_dotenv
from streamlit_autorefresh import st_autorefresh
import threading
from src.storage.models import get_engine, init_db
from src.storage.queries import get_tracked_tickers, get_latest_prices, get_latest_metrics, get_latest_metric_snapshot
from src.ingestion.scheduler import poll_all_tickers
from src.processing.pipeline import process_all_tickers
from apscheduler.schedulers.background import BackgroundScheduler

load_dotenv()

st.set_page_config(page_title="Live Stock Pipeline Dashboard", layout="wide")
TICKERS = os.getenv("TICKERS", "AAPL").split(",")

DB_PATH = os.getenv("DB_PATH", "data/prices.db")
engine = get_engine(DB_PATH)
init_db(engine)

def poll_and_process() : 
    poll_all_tickers()
    process_all_tickers(engine, TICKERS)

if "scheduler_started" not in st.session_state:
    POLL_INTERVAL = int(os.getenv("POLL_INTERVAL_SECONDS", "60"))
    bg_scheduler = BackgroundScheduler()
    bg_scheduler.add_job(poll_and_process, "interval", seconds=POLL_INTERVAL)
    bg_scheduler.start()
    poll_and_process()
    st.session_state["scheduler_started"] = True

st_autorefresh(interval=30_000, key="datarefresh")

st.title("Real-Time Stock Data Dashboard")
st.caption("Live-updating view of prices and derived metrics from the ingestion pipeline")

tickers = get_tracked_tickers(engine)

if not tickers:
    st.warning("No data yet. Make sure the scheduler (src/ingestion/scheduler.py) has run at least once.")
    st.stop()

selected_ticker = st.selectbox("Select a ticker", tickers)

snapshot = get_latest_metric_snapshot(engine, selected_ticker)

if snapshot is None:
    st.info("No processed metrics yet for this ticker. Run scripts/run_processing.py first.")
    st.stop()

# --- Summary cards ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("Latest Close", f"${snapshot.close:,.2f}")
col2.metric("SMA (5)", f"${snapshot.sma_5:,.2f}" if snapshot.sma_5 else "—")
col3.metric(
    "Momentum (5-period)",
    f"{snapshot.momentum_pct:+.2f}%" if snapshot.momentum_pct is not None else "—"
)
col4.metric("Volatility", f"{snapshot.volatility:.3f}" if snapshot.volatility is not None else "—")

st.caption(f"Last updated: {snapshot.timestamp}")

# --- Price chart ---
metrics = get_latest_metrics(engine, selected_ticker, limit=200)

if metrics:
    df = pd.DataFrame([{
        "timestamp": m.timestamp,
        "close": m.close,
        "sma_5": m.sma_5,
        "sma_20": m.sma_20,
    } for m in metrics])

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["timestamp"], y=df["close"], mode="lines", name="Close Price"))
    fig.add_trace(go.Scatter(x=df["timestamp"], y=df["sma_5"], mode="lines", name="SMA (5)"))
    fig.add_trace(go.Scatter(x=df["timestamp"], y=df["sma_20"], mode="lines", name="SMA (20)"))

    fig.update_layout(
        title=f"{selected_ticker} — Price & Moving Averages",
        xaxis_title="Time",
        yaxis_title="Price (USD)",
        height=500,
        hovermode="x unified",
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Not enough data yet to plot a chart.")

# --- Raw data table (collapsible) ---
with st.expander("View raw data"):
    st.dataframe(df if metrics else pd.DataFrame(), use_container_width=True)