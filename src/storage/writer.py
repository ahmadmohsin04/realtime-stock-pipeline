import logging
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from src.storage.models import PriceRecord
from src.ingestion.schemas import PriceTick

logger = logging.getLogger(__name__)

def save_tick (engine, tick: PriceTick) :
    with Session(engine) as session :
        record = PriceRecord(
            ticker = tick.ticker,
            timestamp = tick.timestamp,
            open = tick.open,
            high = tick.high,
            low = tick.low,
            close = tick.close,
            volume = tick.volume,
        )

        session.add(record)
        try : 
            session.commit()
            logger.info(f"Saved {tick.ticker} @ {tick.timestamp}")
        except IntegrityError:
            session.rollback()
            logger.debug (f"Skipped duplicate {tick.ticker} @ {tick.timestamp}")