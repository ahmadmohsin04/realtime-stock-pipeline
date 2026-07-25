import logging
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from src.storage.models import PriceRecord, ProcessedMetric
from src.processing.calculator import compute_metrics

logger = logging.getLogger(__name__)

def load_prices_as_df(engine, ticker : str) -> pd.DataFrame : 
    with Session(engine) as session : 
        rows = session.execute(
            select(PriceRecord).where(PriceRecord.ticker == ticker)
        ).scalars().all()

    if not rows : 
        return pd.DataFrame()
    
    return pd.DataFrame([{
        "ticker" : r.ticker,
        "timestamp" : r.timestamp,
        "close" : r.close,
    }for r in rows])

def save_metrics (engine,df:pd.DataFrame) : 
    saved,skipped = 0,0
    with Session(engine) as session : 
        for _,row in df.iterrows():
            metric = ProcessedMetric(
                ticker = row["ticker"],
                timestamp = row["timestamp"],
                close = row["close"],
                sma_5 = row["sma_5"],
                sma_20 = row["sma_20"],
                momentum_pct = row["momentum_pct"] if pd.notna (row["momentum_pct"]) else None,
                volatility = row ["volatility"] if pd.notna(row["volatility"]) else None,
            )
            session.add(metric)
            try:
                session.commit()
                saved +=1
            except IntegrityError : 
                session.rollback()
                skipped +=1
    logger.info (f"Metrics saved : {saved}, skipped (already existed) : {skipped}")

def process_ticker(engine, ticker : str) : 
    logger.info (f"Processing {ticker}...")
    df = load_prices_as_df(engine,ticker)
    if df.empty :
        logger.warning (f"No raw data found for {ticker}, skipping")
        return
    df_with_metrics = compute_metrics(df)
    save_metrics (engine, df_with_metrics)

def process_all_tickers (engine, tickers : list [str]):
    for ticker in tickers : 
        process_ticker(engine, ticker.strip())
    