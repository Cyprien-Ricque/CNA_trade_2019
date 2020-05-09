#!/usr/bin/python3.7

from src.Parser import Parser
from src.Strategy import Strategy
from src.Indicators import Indicators
from src.Wallet import Wallet
from src.Utils import d_print
import os
import sys


class Trader:
    def __init__(self):
        self.parser_ = Parser(2000)
        self.strategy_ = Strategy()
        self.wallet_ = Wallet(None)
        self.save_ = os.dup(1)

    def run(self):
        os.dup2(2, 1)
        self.parser_.getNextLine()
        data = self.parser_.getData()

        if self.parser_.getDataType() == 'candle':
            self.strategy_.newData(data['USDT_ETH'])
            self.wallet_.updateLinks(data)
            self.strategy_.calcIndicators()

        if self.parser_.getDataType() == 'stack':
            self.wallet_.updateWallet(data)

        if self.parser_.getDataType() == 'action':
            self.strategy_.train()
            os.dup2(self.save_, 1)
            os.write(1, self.strategy_.predict(self.wallet_).encode())
            os.dup2(2, 1)


# Engine out: 'bot 0 send update game next_candles BTC_ETH,1516147200,0.095,0.09181,0.09219501,0.09199999,481.51276914;USDT_ETH,1516147200,1090.1676815,1022.16791604,1023.1,1029.99999994,1389783.7868468;USDT_BTC,1516147200,11600.12523891,11032.9211865,11041.42197477,11214.06052489,4123273.6568455'
