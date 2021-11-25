import yfinance as yf


def get_data(ticker, period, interval):
    data = yf.download(ticker, period=period, interval=interval)
    return data


class Backtest:
    def __init__(self, initial_deposit: float, initial_asset: float, ticker: str, period: str, interval: str):
        self.cash = initial_deposit
        self.asset = initial_asset
        self.data = get_data(ticker, period, interval)
        self._open = 0
