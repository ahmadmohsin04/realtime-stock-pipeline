import os
import logging
from dotenv import load_dotenv
from apscheduler.schedulers.blocking import BlockingScheduler
from src.ingestion.fetcher import fetch_latest_tick
from src.storage.models import  get_engine, init_db
from src.storage.writer import save_tick

load_dotenv()

formatter = logging.Formatter ("%(asctime)s [%(levelname)s] %(message)s")

file_handler = logging.FileHandler ("logs/pipeline.log")
file_handler.setFormatter(formatter)

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
root_logger.addHandler(file_handler)
root_logger.addHandler(console_handler)

logger = logging.getLogger (__name__)

TICKERS = os.getenv("TICKERS", "AAPL").split(",")
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL_SECONDS", "60"))
DB_PATH = os.getenv("DB_PATH", "data/prices.db")

engine = get_engine (DB_PATH)
init_db (engine)

def poll_all_tickers():
    logger.info (f"Polling {len(TICKERS)} tickers : {TICKERS}")
    for ticker in TICKERS :
        tick = fetch_latest_tick(ticker.strip())
        if tick : 
            save_tick(engine, tick)
        else : 
            logger.warning (f"Skipped {ticker} this cycle (no valid data)")


if __name__ == "__main__" : 
    scheduler = BlockingScheduler()
    scheduler.add_job(poll_all_tickers, "interval", seconds = POLL_INTERVAL)
    logger.info(f"Starting scheduler : polling every {POLL_INTERVAL}s")
    poll_all_tickers()
    try :
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info ("Scheduler Stoped.")