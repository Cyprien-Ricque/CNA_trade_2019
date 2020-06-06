#!/usr/bin/python3.7

from src.Parser import Parser
from src.Strategy import Strategy
from src.Wallet import Wallet
import os


class Trader:
    def __init__(self):
        self.startCalc = -350
        self.startAddData = -350
        self.startUpdateWallet = -3
        self.parser_ = Parser()

        # === Update model === #
        self.updateModel_ = False
        self.reDoModel_ = False
        # ==================== #

        self.pair_ = ('USDT', 'BTC')
        self.strategy_ = Strategy(self.updateModel_, self.pair_)
        self.reference_ = 'USDT'
        self.wallet_ = Wallet(None, self.reference_)

        self.reDoModel_ = self.updateModel_ if self.updateModel_ is False else self.reDoModel_
        if self.reDoModel_ is True:
            self.strategy_.removeTrainedModel()


        # === CONSTANT === #
        self.save_ = os.dup(1)
        self.trainTime_ = True
        self.startIter = None
        self.currentIter = 0
        self.saveStdout = os.dup(1)
        os.dup2(2, 1)
        # ================ #

    def run(self):
        self.parser_.getNextLine()
        data = self.parser_.getData()

        if self.parser_.getDataType() == 'candle':
            self.currentIter += 1
            if self.currentIter >= self.startIter + self.startUpdateWallet:
                self.wallet_.updateLinks(data)
            if self.currentIter >= self.startIter + self.startAddData or self.updateModel_ is True:
                self.strategy_.newData(data[self.pair_[0] + '_' + self.pair_[1]])
                if self.currentIter > self.startIter + self.startCalc or self.updateModel_:
                    self.strategy_.calcIndicators()
            return

        if self.parser_.getDataType() == 'stack':
            self.wallet_.updateWallet(data)
            return

        if self.parser_.getDataType() == 'action':
            if self.updateModel_ is True and self.trainTime_ is True:
                self.strategy_.train()
                self.trainTime_ = False
            os.write(self.saveStdout, self.strategy_.predict(self.wallet_).encode())

        if self.parser_.getDataType() == 'setting':
            if 'transaction_fee_percent' in self.parser_.setting().keys():
                self.wallet_.setFee(self.parser_.setting()['transaction_fee_percent'])
            if 'candles_given' in self.parser_.setting().keys() and self.startIter is None:
                self.startIter = int(self.parser_.setting()['candles_given'][0])
            if 'initial_stack' in self.parser_.setting().keys():
                self.wallet_.setInitialStack(int(self.parser_.setting()['initial_stack'][0]))
            return
