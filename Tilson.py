import pandas as pd
import matplotlib.pyplot as plt
from Backtest import Backtest

plt.rcParams['figure.figsize'] = (20, 10)
plt.style.use('fivethirtyeight')


class Tilson(Backtest):
    def __init__(self, initial_deposit: float, initial_asset: float, ticker: str, period: str, interval: str, length: int, vol_fac: float):
        super().__init__(initial_deposit, initial_asset, ticker, period, interval)
        self.sdata = self.get_tilson_data(length, vol_fac)
        self.portfolio = self.calculate_portfolio()

    def get_tilson(self, length, vol_fac):
        price = (self.data['High'] + self.data['Low'] + self.data['Close']) / 3
        exp1 = price.ewm(span=length, adjust=False).mean()
        exp2 = exp1.ewm(span=length, adjust=False).mean()
        exp3 = exp2.ewm(span=length, adjust=False).mean()
        exp4 = exp3.ewm(span=length, adjust=False).mean()
        exp5 = exp4.ewm(span=length, adjust=False).mean()
        exp6 = exp5.ewm(span=length, adjust=False).mean()
        c1 = -(vol_fac * vol_fac * vol_fac)
        c2 = (3 * vol_fac * vol_fac + 3 * vol_fac * vol_fac * vol_fac)
        c3 = (-6*vol_fac*vol_fac-3*vol_fac-3*vol_fac*vol_fac*vol_fac)
        c4 = (1 + 3 * vol_fac + vol_fac * vol_fac * vol_fac + 3 * vol_fac * vol_fac)
        T3 = c1 * exp6 + c2 * exp5 + c3 * exp4 + c4 * exp3

        return T3

    def get_tilson_data(self, length, vol_fac):
        hist = self.data
        t3 = pd.DataFrame(self.get_tilson(length, vol_fac)).rename(columns={0: 'T3'})
        t3_last = t3.shift(periods=1, axis=0, fill_value=0).rename(columns={'T3': 'T3_Last'})
        t3_prev = t3.shift(periods=2, axis=0, fill_value=0).rename(columns={'T3': 'T3_Prev'})
        t3_pprev = t3.shift(periods=3, axis=0, fill_value=0).rename(columns={'T3': 'T3_PPrev'})
        return pd.concat([t3, t3_last, t3_prev, t3_pprev, hist], join='inner', axis=1)

    def calculate_portfolio(self):
        hist = self.sdata
        cashDf = hist.apply(self.manage_position, raw=False, axis=1)
        return cashDf

    def manage_position(self, x):
        if x[1] > x[2] and x[2] < x[3]:
            if not self._open:
                self.asset = float(self.cash / x[7])
                self.entry = float(self.asset * x[7])
                self.cash = 0
                self._open = True
        elif x[1] < x[2] and x[2] > x[3]:
            if self._open:
                self.cash = float(self.asset * x[7])
                self.asset = 0
                self._open = False

        # if float(self.asset * x[6]) <= (85/100)*self.entry:
        #     if self.cash == 0:
        #         self.cash = float(self.asset * x[7])
        #         self.asset = 0
        #         self._open = False

        return float(self.cash + self.asset * x[7])

    def manage_oc(self, x):
        if x[1] > x[2] and x[2] < x[3]:
            self._open = True
        elif x[1] < x[2] and x[2] > x[3]:
            self._open = False

        return self._open

    def get_tilson_oc(self):
        return self.sdata.apply(self.manage_oc, raw=False, axis=1)

    def plot_strat(self):
        hist = self.sdata
        prices = hist['Close']

        ax1 = plt.subplot2grid((11, 1), (0, 0), rowspan=5, colspan=1)
        ax2 = plt.subplot2grid((11, 1), (6, 0), rowspan=5, colspan=1)

        ax1.plot(prices, linewidth=1.5, label=['Price'])
        ax1.plot(hist['T3'], linewidth=1.5, label=['Tilson T3'])
        ax2.plot(self.portfolio, color='black', linewidth=1.5, label='Cash')

        plt.legend(loc='lower right')
