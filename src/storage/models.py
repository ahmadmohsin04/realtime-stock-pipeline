from sqlalchemy import Column, Integer, String, Float, DateTime,UniqueConstraint,Index, create_engine
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class PriceRecord(Base):
    __tablename__ = "price_records"
    __table_args__ = (
        UniqueConstraint("ticker", "timestamp", name = "uq_ticker_timestamp"),
        Index("ix_ticker_timestamp_desc", "ticker", "timestamp")
        
        )

    id = Column (Integer, primary_key = True, autoincrement = True)
    ticker = Column(String,nullable = False, index = True)
    timestamp = Column(DateTime, nullable = False, index = True)
    open = Column (Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Float)
    fetched_at = Column (DateTime, default = datetime.utcnow)

class ProcessedMetric(Base):
    __tablename__ = "processed_metrics"
    __table_args__ = (
        UniqueConstraint("ticker","timestamp", name = "uq_metric_ticker_timestamp"),
        Index("ix_metric_ticker_timestamp_desc", "ticker", "timestamp")
        )
    id = Column (Integer, primary_key = True, autoincrement = True)
    ticker = Column (String, nullable = False, index = True)
    timestamp = Column (DateTime, nullable = False, index = True)
    close = Column(Float)
    sma_5 = Column(Float)
    sma_20 = Column(Float)
    momentum_pct = Column(Float)
    volatility = Column (Float)
    computed_at = Column (DateTime, default = datetime.utcnow)




def get_engine(db_path="data/prices.db"):
    return create_engine(f"sqlite:///{db_path}")

def init_db (engine) :
    Base.metadata.create_all(engine)