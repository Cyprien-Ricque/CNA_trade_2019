#!/usr/bin/python3.7

from src.Indicators import Indicators
import pandas as pd
import sys


class Strategy:
    def __init__(self):
        self._data = None
        self._indicators = Indicators(40)

    def newData(self, data):
        if self._data is None:
            self._data = pd.DataFrame(data)
        else:
            self._data = pd.concat([self._data, pd.DataFrame(data)], ignore_index=True)

    def calcIndicators(self):
        self._indicators.calcIndicators(self._data, ['current', 'MMA', 'MME'])

    def train(self):
        pass

    def predict(self, wallet):
        self.calcIndicators()
        if self._indicators.getIndicators()['MMA'][-1] > self._indicators.getIndicators()['current'][-1] and \
                wallet.haveEnough(buy=False, pair=('USDT', 'ETH'), amount=0.01):
            return 'sell USDT_ETH 0.001\n'
        if self._indicators.getIndicators()['MMA'][-1] < self._indicators.getIndicators()['current'][-1] and \
                wallet.haveEnough(buy=True, pair=('USDT', 'ETH'), amount=0.01):
            return 'buy USDT_ETH 0.001\n'
        return 'pass\n'
