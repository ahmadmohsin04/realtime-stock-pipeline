import pytest
import sys
sys.path.append(".")
from datetime import datetime
from pydantic import ValidationError
from src.ingestion.schemas import PriceTick


def test_valid_tick_is_accepted():
    tick = PriceTick(
        ticker="AAPL", timestamp=datetime.now(),
        open=100.0, high=101.0, low=99.0, close=100.5, volume=1000.0
    )
    assert tick.ticker == "AAPL"


def test_zero_close_price_is_rejected():
    with pytest.raises(ValidationError):
        PriceTick(
            ticker="AAPL", timestamp=datetime.now(),
            open=100.0, high=101.0, low=99.0, close=0.0, volume=1000.0
        )


def test_negative_close_price_is_rejected():
    with pytest.raises(ValidationError):
        PriceTick(
            ticker="AAPL", timestamp=datetime.now(),
            open=100.0, high=101.0, low=99.0, close=-5.0, volume=1000.0
        )