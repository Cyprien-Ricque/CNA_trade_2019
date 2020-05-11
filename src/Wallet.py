import sys
import os


class Wallet:
    def __init__(self, wallet):
        self._wallet = wallet if wallet is not None else {}
        self._candles = {}
        self.fee_ = 0

    def updateWallet(self, wallet):
        for m in wallet:
            self._wallet[m] = wallet[m]

    def setFee(self, fee):
        self.fee_ = fee

    def updateLinks(self, candles):
        for m in candles:
            # print(m, file=sys.stderr)
            self._candles[m] = candles[m]['close'][0]

    def haveEnough(self, buy, pair, amount):
        if buy is True:
            amount = amount * self._candles[str(pair[0]) + '_' + str(pair[1])]

        if amount > self._wallet[pair[0]] and buy is True:
            return False
        if amount > self._wallet[pair[1]] and buy is False:
            return False
        return True

    def sell(self, pair, percent=5):
        return str(self._wallet[pair[1]] * (percent / 100))

    def buy(self, pair, percent=5):
        return str((self._wallet[pair[0]] * (percent / 100)) / self._candles[str(pair[0]) + '_' + str(pair[1])])

