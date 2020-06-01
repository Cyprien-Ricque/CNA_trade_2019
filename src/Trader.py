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
        self.updateModel_ = True
        self.strategy_ = Strategy(self.updateModel_)
        self.reDoModel_ = True
        if self.reDoModel_ is True:
            self.strategy_.removeTrainedModel()
        self.wallet_ = Wallet(None)
        self.save_ = os.dup(1)
        self.trainTime_ = True
        self.startIter = None
        self.startCalc = -200
        self.startAddData = -240
        self.currentIter = 0

    def run(self):
        self.parser_.getNextLine()
        data = self.parser_.getData()

        if self.parser_.getDataType() == 'setting':
            if 'transaction_fee_percent' in self.parser_.setting().keys():
                self.wallet_.setFee(self.parser_.setting()['transaction_fee_percent'])
            if 'candles_given' in self.parser_.setting().keys() and self.startIter is None:
                self.startIter = int(self.parser_.setting()['candles_given'][0])
            if 'initial_stack' in self.parser_.setting().keys():
                self.wallet_.setInitialStack(int(self.parser_.setting()['initial_stack'][0]))
            return

        if self.parser_.getDataType() == 'candle':
            self.currentIter += 1
            if self.currentIter >= self.startIter + self.startAddData or self.updateModel_ is True:
                self.strategy_.newData(data['USDT_ETH'])
                self.wallet_.updateLinks(data)
                if self.currentIter > self.startIter + self.startCalc or self.updateModel_:
                    self.strategy_.calcIndicators()
            return

        if self.parser_.getDataType() == 'stack':
            self.wallet_.updateWallet(data)
            return

        if self.parser_.getDataType() == 'action':
            if self.trainTime_ is True and self.updateModel_ is True:
                print("TRAIN")
                self.strategy_.train()
                print("TRAIN END")
                self.trainTime_ = False
            print("PREDICT")
            os.dup2(self.save_, 1)
            os.write(1, self.strategy_.predict(self.wallet_).encode())
            os.dup2(2, 1)
            print("PREDICT END")


# Engine out: 'bot 0 send update game next_candles BTC_ETH,1516147200,0.095,0.09181,0.09219501,0.09199999,481.51276914;USDT_ETH,1516147200,1090.1676815,1022.16791604,1023.1,1029.99999994,1389783.7868468;USDT_BTC,1516147200,11600.12523891,11032.9211865,11041.42197477,11214.06052489,4123273.6568455'



