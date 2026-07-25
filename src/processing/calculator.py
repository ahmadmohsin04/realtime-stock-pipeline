import pandas as pd

def compute_metrics (df : pd.DataFrame) -> pd.DataFrame:
    """
    Takes a DataFrame of raw price records for ONE ticker, sorted by timestamp,
    and returs a DataFrame with a derived metrics added.
    Expects columns : ticker, timestamp, close
    """

    df = df.sort_values("timestamp").copy()
    df["sma_5"] = df["close"].rolling(window = 5, min_periods = 1).mean()
    df["sma_20"] = df["close"].rolling(window = 20, min_periods = 1).mean()
    df["momentum_pct"] = df["close"].pct_change(periods = 5) * 100
    df["volatility"] = df["close"].rolling(window = 10, min_periods = 2).std()

    return df
