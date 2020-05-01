#!/usr/bin/python3.7

from Parser import Parser
from Strategy import Strategy
from Indicators import Indicators
from Wallet import Wallet
from Utils import d_print
import os
import sys


class Trader:
    def __init__(self):
        self._parser = Parser(2000)
        self._strategy = Strategy()
        self._wallet = Wallet(None)

    def run(self):
        self._parser.getNextLine()
        data = self._parser.getData()

        if self._parser.getDataType() == 'candle':
            self._strategy.newData(data['USDT_ETH'])
            self._wallet.updateLinks(data)

        if self._parser.getDataType() == 'stack':
            self._wallet.updateWallet(data)

        if self._parser.getDataType() == 'action':
            print("Action !", file=sys.stderr, flush=True)
            os.write(1, self._strategy.predict(self._wallet).encode())
