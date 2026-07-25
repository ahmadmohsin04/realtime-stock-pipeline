import yfinance as yf
import logging
from datetime import datetime
from src.ingestion.schemas import PriceTick

logger = logging.getLogger(__name__)

def fetch_latest_tick(ticker:str) -> PriceTick | None :
    """Fetch the most recent 1-minute price bar for a ticker."""
    try :
        data = yf.Ticker(ticker).history(period="1d", interval = "1m")
        if data.empty:
            logger.warning(f"No data returned for {ticker}")
            return None
        
        latest = data.iloc[-1]
        return PriceTick(
            ticker= ticker,
            timestamp = data.index[-1].to_pydatetime(),
            open = latest["Open"],
            high = latest["High"],
            low = latest["Low"],
            close = latest["Close"],
            volume = latest["Volume"],
            
        )

    except Exception as e :
        logger.error(f"Failed to fetch {ticker} : {e}")
        return None