import sys
sys.path.append(".")
from src.storage.models import get_engine, init_db

engine = get_engine()
init_db (engine)
print("Database initialized at data/prices.db")