import pandas as pd
import matplotlib.pyplot as plt
from Backtest import Backtest

plt.rcParams['figure.figsize'] = (20, 10)
plt.style.use('fivethirtyeight')


class Macd(Backtest):
    def __init__(self, initial_deposit: float, initial_asset: float, ticker: str, period: str, interval: str, fast: int, slow: int, smooth: int):
        super().__init__(initial_deposit, initial_asset, ticker, period, interval)
        self.mcdata = self.get_macd(fast, slow, smooth)
        self.portfolio = self.calculate_portfolio()

    def get_macd(self, fast, slow, smooth):
        price = self.data['Close']
        exp1 = price.ewm(span=fast, adjust=False).mean()
        exp2 = price.ewm(span=slow, adjust=False).mean()
        macd = pd.DataFrame(exp1 - exp2).rename(columns={'Close': 'MACD'})
        signal = pd.DataFrame(macd.ewm(span=smooth, adjust=False).mean()).rename(columns={'MACD': 'Signal'})

        return pd.concat([macd, signal, self.data], join='inner', axis=1)

    def calculate_portfolio(self):
        hist = self.mcdata
        cashDf = hist.apply(self.manage_position, raw=False, axis=1)
        return cashDf

    def manage_position(self, x):
        if x[0] > x[1]:
            if self.cash > 0:
                self.asset = float(self.cash / x[5])
                self.cash = 0
            return float(self.cash + self.asset * x[5])
        else:
            if self.cash == 0:
                self.cash = float(self.asset * x[5])
                self.asset = 0
            return float(self.cash + self.asset)

    def plot_macd(self):
        hist = self.mcdata
        prices = hist['Close']
        macd = hist['MACD']
        signal = hist['Signal']

        ax1 = plt.subplot2grid((16, 1), (0, 0), rowspan=5, colspan=1)
        ax2 = plt.subplot2grid((16, 1), (6, 0), rowspan=3, colspan=1)
        ax3 = plt.subplot2grid((16, 1), (10, 0), rowspan=5, colspan=1)

        ax1.plot(prices, linewidth=1.5)
        ax2.plot(macd, color='blue', linewidth=1.5, label='MACD')
        ax2.plot(signal, color='orange', linewidth=1.5, label='Signal')
        ax3.plot(self.portfolio, color='black', linewidth=1.5, label='Cash')

        plt.legend(loc='lower right')
