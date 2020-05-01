#!/usr/bin/python3.7

from Indicators import Indicators
import pandas as pd
import sys


class Strategy:
    def __init__(self):
        self._data = None
        self._indicators = Indicators(30)

    def newData(self, data):
        if self._data is None:
            self._data = pd.DataFrame(data)
        else:
            self._data = pd.concat([self._data, pd.DataFrame(data)], ignore_index=True)

    def calcIndicators(self):
        self._indicators.calcIndicators(self._data, ['current', 'mean'])

    def train(self):
        pass

    def predict(self, wallet):
        self.calcIndicators()
        if self._indicators.getIndicators()['mean'] > self._indicators.getIndicators()['current'] and \
                wallet.haveEnough(buy=False, pair=('USDT', 'ETH'), amount=0.01):
            return 'sell USDT_ETH 0.01\n'
        if self._indicators.getIndicators()['mean'] < self._indicators.getIndicators()['current'] and \
                wallet.haveEnough(buy=True, pair=('USDT', 'ETH'), amount=0.01):
            return 'buy USDT_ETH 0.01\n'
        return 'pass\n'
