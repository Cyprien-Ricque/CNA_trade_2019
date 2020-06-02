import sys
import os


class Wallet:
    def __init__(self, wallet):
        self.wallet_ = wallet if wallet is not None else {}
        self.candles_ = {}
        self.fee_ = 0
        self.initialStack_ = {}

    def updateWallet(self, wallet):
        for m in wallet:
            self.wallet_[m] = wallet[m]

    def setFee(self, fee):
        self.fee_ = fee

    def setInitialStack(self, IS):
        self.initialStack_['USDT'] = IS

    def updateLinks(self, candles):
        for m in candles:
            self.candles_[m] = candles[m]['close']

    def haveEnough(self, buy, pair, amount):
        if buy is True:
            amount = amount * self.candles_[str(pair[0]) + '_' + str(pair[1])]
        if amount > self.wallet_[pair[0]] and buy is True:
            return False
        if amount > self.wallet_[pair[1]] and buy is False:
            return False
        return True

    def sell(self, pair, percent=5):
        max = self.initialStack_['USDT']
        sell = (max * (percent / 100)) / self.candles_[str(pair[0]) + '_' + str(pair[1])]
        sell = sell if sell < self.wallet_[pair[1]] else self.wallet_[pair[1]]
        return str(sell) + '\n'

    def buy(self, pair, percent=5):
        max = self.initialStack_['USDT']
        buy = max * (percent / 100) if max * (percent / 100) < self.wallet_[pair[0]] else self.wallet_[pair[0]]
        buy /= self.candles_[str(pair[0]) + '_' + str(pair[1])]
        return str(buy) + '\n'

