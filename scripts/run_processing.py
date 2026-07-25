import sys
sys.path.append(".")
import os
import logging
from dotenv import load_dotenv
from src.storage.models import get_engine, init_db
from src.processing.pipeline import process_all_tickers

load_dotenv()

logging.basicConfig(level = logging.INFO, format = "%(asctime)s [%(levelname)s] %(message)s")

TICKERS = os.getenv("TICKERS", "AAPL").split(",")
DB_PATH = os.getenv ("DB_PATH", "data/prices.db")

engine = get_engine (DB_PATH)
init_db(engine)

process_all_tickers(engine, TICKERS)
