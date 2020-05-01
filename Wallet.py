import sys
import os


class Wallet:
    def __init__(self, wallet):
        self._wallet = wallet if wallet is not None else {}
        self._candles = {}

    def updateWallet(self, wallet):
        for m in wallet:
            self._wallet[m] = wallet[m]

    def updateLinks(self, candles):
        for m in candles:
            print(m, file=sys.stderr)
            self._candles[m] = candles[m]['close'][0]

    def haveEnough(self, buy, pair, amount):
        if buy is True:
            amount = amount * self._candles[str(pair[0]) + '_' + str(pair[1])]
        print('AMOUNT', buy, amount, file=sys.stderr)
        if amount > self._wallet[pair[0]] and buy is True:
            return False
        if amount > self._wallet[pair[1]] and buy is False:
            return False
        return True

