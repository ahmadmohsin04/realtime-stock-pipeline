import pandas as pd
import sys
sys.path.append(".")
from src.processing.calculator import compute_metrics


def make_price_df(closes):
    """Helper: build a minimal price DataFrame from a list of close prices."""
    timestamps = pd.date_range("2026-01-01", periods=len(closes), freq="1min")
    return pd.DataFrame({
        "ticker": ["TEST"] * len(closes),
        "timestamp": timestamps,
        "close": closes,
    })


def test_sma_5_equals_close_with_one_point():
    df = make_price_df([100.0])
    result = compute_metrics(df)
    assert result.iloc[0]["sma_5"] == 100.0


def test_sma_5_is_correct_rolling_average():
    df = make_price_df([100, 102, 104, 106, 108])
    result = compute_metrics(df)
    # last row: average of all 5 points
    assert result.iloc[-1]["sma_5"] == 104.0


def test_momentum_is_none_with_fewer_than_6_points():
    df = make_price_df([100, 101, 102, 103, 104])
    result = compute_metrics(df)
    assert pd.isna(result.iloc[-1]["momentum_pct"])


def test_momentum_calculates_correct_percent_change():
    df = make_price_df([100, 101, 102, 103, 104, 110])
    result = compute_metrics(df)
    # (110 - 100) / 100 * 100 = 10.0%
    assert round(result.iloc[-1]["momentum_pct"], 2) == 10.0


def test_volatility_is_none_with_one_point():
    df = make_price_df([100.0])
    result = compute_metrics(df)
    assert pd.isna(result.iloc[0]["volatility"])


def test_volatility_is_positive_with_varying_prices():
    df = make_price_df([100, 105, 95, 110, 90])
    result = compute_metrics(df)
    assert result.iloc[-1]["volatility"] > 0


def test_output_preserves_row_count():
    df = make_price_df([100, 101, 102])
    result = compute_metrics(df)
    assert len(result) == len(df)