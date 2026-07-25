import yfinance as yf

def test_fetch_ticker():
    ticker = yf.Ticker("AAPL")
    data = ticker.history(period="1d", interval = "1m")
    assert not data.empty
    print(data.tail())

if __name__ == "__main__":
    test_fetch_ticker()

    