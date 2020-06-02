import os
import sys
import pandas as pd
import numpy as np


class Indicators:
    def __init__(self, period, indicators):
        self.indicators_ = pd.DataFrame([[0 for i in indicators]], columns=indicators)
        self.period_ = period
        self.indList_ = indicators
        self.data_ = pd.DataFrame()
        self.iter_ = 1
        self.actionsStarted_ = False
        self.scaleValues_ = {}

    def getPeriod(self):
        return self.period_

    def addData(self, newData):
        self.data_.append(pd.DataFrame(newData))

    def getScaleValues(self):
        return self.scaleValues_

    def getIndicatorsList(self):
        return self.indList_

    def getIndicators(self, cols):
        df = pd.DataFrame(self.indicators_)
        return df.loc[:, cols]

    def getIndicators_PP(self):
        return self.indicators_.iloc[:, list(pd.Series(list(self.indicators_.columns)).str.contains('PP'))]

    def indUnknown(self, ind):
        print("Indicator \"" + ind + "\" unknown", flush=True, file=sys.stderr)
        print("Indicators available : ", file=sys.stderr, end='')
        for ind in self.indList_:
            print(ind, file=sys.stderr, end='')
            if ind != self.indList_[-1]:
                print(', ', file=sys.stderr, end='')
        print("\n", end='', file=sys.stderr)

    def preprocess(self):
        self.actionsStarted_ = True

        for c in self.indicators_.columns:
            self.scaleValues_[c + '_min'] = self.indicators_.loc[:, c].min()
            self.scaleValues_[c + '_max'] = self.indicators_.loc[:, c].max()
            self.indicators_.loc[:, c + '_PP'] = self.indicators_.loc[:, c].apply(lambda x: (x - self.scaleValues_[c + '_min']) / self.scaleValues_[c + '_max'])

    def isFirstActionPassed(self):
        return self.actionsStarted_

    def calcIndicators(self, data):
        self.iter_ += 1
        self.data_ = data
        self.indicators_ = self.indicators_.append(pd.Series([0 for i in self.indicators_.columns], index=self.indicators_.columns), ignore_index=True)
        if data.shape[0] < 2:
            return

        for ind in self.indList_:
            getattr(self, ind, self.indUnknown)(ind)
            if self.actionsStarted_ is True:
                self.indicators_.loc[:, ind + '_PP'].iloc[-1] = (self.indicators_.loc[:, ind].iloc[-1] - self.scaleValues_[ind + '_min']) / self.scaleValues_[ind + '_max']

    def current(self, ind):
        self.indicators_.current.iloc[-1] = self.data_.close.iloc[-1]

    def evolution(self, ind):
        self.indicators_.evolution.iloc[-1] = self.data_.close.iloc[-1] - self.data_.close.iloc[-2]
        # self.indicators_.loc[:, 'evolution%'].iloc[-1] = (self.indicators_.evolution.iloc[-1] * 100 /
        #     (self.data_.close.iloc[-self.period_:].max() - self.data_.close.iloc[-self.period_:].min()))

    def MMA(self, ind):
        self.indicators_.MMA.iloc[-1] = self.data_.close.iloc[-self.period_:].mean()

    def MME(self, ind=None):
        C = self.data_.close.iloc[-1]
        K = 2 / (self.period_ + 1)
        self.indicators_.MME.iloc[-1] = C - (self.indicators_.MME.iloc[-2]) * K + (self.indicators_.MME.iloc[-2])

    def MMP(self, ind):
        P = self.period_ if self.data_.close.__len__() >= self.period_ else self.data_.close.__len__()
        S = np.array([(P - i) * self.data_.close.iloc[-i] for i in range(1, P)]).sum()
        self.indicators_.MMP.iloc[-1] = S / (P * (P + 1) / 2)

    def MML(self, ind):
        self.indicators_.MMP.iloc[-1] = self.data_.close.iloc[-1] - (self.indicators_.MML.iloc[-2]) * (1 / self.period_) + (self.indicators_.MML.iloc[-2])

    # FIXME Faire les 2 périodes pour le MACD

    def MACD(self, ind):
        self.indicators_.MACD.iloc[-1] = 1
        # self.indicators_.MACD.iloc[-1] = self.indicators_.MME.iloc[-1] - self.indicators_.MME.iloc[-1]

    def RSI(self, ind):
        S = self.indicators_.evolution.iloc[-self.period_:]
        H = S[S > 0].mean()
        B = S[S < 0].mean()
        self.indicators_.RSI.iloc[-1] = 100 * H / (H - B)

    # TODO faire la diff entre les 2

    def BLG_UP(self, ind):
        std = self.data_.close.iloc[-self.period_:].std()
        self.indicators_.BLG_UP.iloc[-1] = self.indicators_.MME.iloc[-1] + std * 2

    def BLG_DOWN(self, ind):
        std = self.data_.close.iloc[-self.period_:].std()
        self.indicators_.BLG_DOWN.iloc[-1] = self.indicators_.MME.iloc[-1] - std * 2

