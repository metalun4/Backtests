import pandas as pd
import matplotlib.pyplot as plt
from Backtest import Backtest
from Tilson import Tilson
from Wtlb import Wtlb

plt.rcParams['figure.figsize'] = (20, 10)
plt.style.use('fivethirtyeight')


class Multi:
    def __init__(self, initial_deposit: float, initial_asset: float, ticker: str, period: str, interval: str, length: int, vol_fac: float, clength: int, alength: int):
        self.tilson = Tilson(initial_deposit, initial_asset, ticker, period, interval, length, vol_fac)
        self.tilson_oc = self.tilson.get_tilson_oc()
        self.wtlb = Wtlb(initial_deposit, initial_asset, ticker, period, interval, clength, alength)
        self.wtlb_oc = self.wtlb.get_wtlb_oc()

        self.cash = initial_deposit
        self.asset = initial_asset
        self._open = 0
        self.entry = 0
        self.portfolio = self.calculate_portfolio()

    def calculate_portfolio(self):
        hist = pd.concat([self.tilson_oc, self.wtlb_oc, self.tilson.data], join='inner', axis=1)
        cashDf = hist.apply(self.manage_position, raw=False, axis=1)
        return cashDf

    def manage_position(self, x):
        if x[0] is True and x[1] is True:
            if not self._open:
                self.asset = float(self.cash / x["Close"])
                self.entry = float(self.asset * x["Close"])
                self.cash = 0
                self._open = True
        elif x[1] is False:
            if self._open:
                self.cash = float(self.asset * x["Close"])
                self.asset = 0
                self._open = False

        return float(self.cash + self.asset * x["Close"])

    def plot_strat(self):
        prices = self.tilson.data['Close']

        ax1 = plt.subplot2grid((11, 1), (0, 0), rowspan=5, colspan=1)
        ax2 = plt.subplot2grid((11, 1), (6, 0), rowspan=5, colspan=1)

        ax1.plot(prices, linewidth=1.5, label=['Price'])

        ax2.plot(self.portfolio, color='black', linewidth=1.5, label='Cash')

        plt.legend(loc='lower right')
