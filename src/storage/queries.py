from sqlalchemy import select, desc
from sqlalchemy.orm import Session
from src.storage.models import PriceRecord, ProcessedMetric


def get_latest_prices (engine, ticker : str, limit : int = 100):
    """Most recent N raw price ticks for a ticker, newest first."""
    with Session (engine) as session : 
        rows = session.execute (
            select(PriceRecord)
            .where(PriceRecord.ticker == ticker)
            .order_by(desc(PriceRecord.timestamp))
            .limit(limit)
        ).scalars().all()
    return list (reversed(rows))

def get_latest_metrics (engine,ticker : str, limit : int = 100):
    """Most recent N processed metric rows for a ticker, newest first."""
    with Session(engine) as session : 
        rows = session.execute(
            select(ProcessedMetric)
            .where(ProcessedMetric.ticker == ticker)
            .order_by(desc(ProcessedMetric.timestamp))
            .limit(limit)
        ).scalars().all()
    return list (reversed(rows))


def get_tracked_tickers (engine) : 
    """Distinct list of tickers that have data"""
    with Session (engine) as session : 
        rows = session.execute(select(PriceRecord.ticker). distinct()).scalars().all()
    return sorted(rows)

def get_latest_metric_snapshot (engine, ticker: str) :
    """Single most recent metric row for a ticker (for summary cards)."""
    with Session (engine) as session : 
        row = session.execute (
            select (ProcessedMetric)
            .where(ProcessedMetric.ticker == ticker)
            .order_by (desc(ProcessedMetric.timestamp))
            .limit(1)
        ).scalars().first()
    return row