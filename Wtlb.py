import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from Backtest import Backtest

plt.rcParams['figure.figsize'] = (20, 10)
plt.style.use('fivethirtyeight')


class Wtlb(Backtest):
    def __init__(self, initial_deposit: float, initial_asset: float, ticker: str, period: str, interval: str, clength: int, alength: int):
        super().__init__(initial_deposit, initial_asset, ticker, period, interval)
        self.wtlbdata = self.get_wtlb(clength, alength)
        self.portfolio = self.calculate_portfolio()

    def get_wtlb(self, clength, alength):
        price = (self.data['High'] + self.data['Low'] + self.data['Close']) / 3
        esa = price.ewm(span=clength, adjust=False).mean()
        pmes = price - esa
        d = np.absolute(pmes).ewm(span=clength, adjust=False).mean()
        ci = pmes / (0.015 * d)
        tci = ci.ewm(span=alength, adjust=False).mean()

        wt1 = pd.DataFrame(tci).rename(columns={0: 'WT1'})
        wt2 = pd.DataFrame(tci.rolling(4).mean()).rename(columns={0: 'WT2'})

        return pd.concat([wt1, wt2, self.data], join='inner', axis=1)

    def calculate_portfolio(self):
        hist = self.wtlbdata
        cashDf = hist.apply(self.manage_position, raw=False, axis=1)
        return cashDf

    def manage_position(self, x):
        if x[1] < x[0] < -53:
            if not self._open:
                self.asset = float(self.cash / x[6])
                self.entry = float(self.asset * x[6])
                self.cash = 0
                self._open = True
        elif x[1] > x[0] > 53:
            if self._open:
                self.cash = float(self.asset * x[6])
                self.asset = 0
                self._open = False

        # if float(self.asset * x[6]) <= (85/100)*self.entry:
        #     if self.cash == 0:
        #         self.cash = float(self.asset * x[6])
        #         self.asset = 0
        #         self._open = False

        return float(self.cash + self.asset * x[6])

    def plot_wtlb(self):
        prices = self.wtlbdata['Close']

        ax1 = plt.subplot2grid((11, 1), (0, 0), rowspan=5, colspan=1)
        ax2 = plt.subplot2grid((11, 1), (6, 0), rowspan=5, colspan=1)

        ax1.plot(prices, linewidth=1.5, label=['Price'])

        ax2.plot(self.portfolio, color='black', linewidth=1.5, label='Cash')

        plt.legend(loc='lower right')
